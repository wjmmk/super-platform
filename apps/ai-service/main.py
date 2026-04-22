from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Query, Body, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import BlogPost, AnalysisRequest, PostResponse, PostCreate, UserResponse, UserCreate, PostUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

import models.models
from database import Base, engine, get_db

# Creacion de la DB and Tables.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Service", version="1.0")

# Routes for Media Files.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Permite usar plantillas HTML desde FastAPI.
templates = Jinja2Templates(directory="templates")

BLOG_POST: BlogPost[dict] = [
    {
        "id": 123,
        "title": "How to Use AI in Your Business",
        "content": "AI can help you automate tasks, analyze data, and improve customer experience"
    },
    {
        "id": 124,
        "title": "The Future of AI in Healthcare",
        "content": "AI is revolutionizing the healthcare industry with new diagnostic tools and treatment options"
    },
    {
        "id": 125,
        "title": "AI and the Future of Work",
        "content": "As AI continues to evolve, it's important to understand how it will impact the job market and what skills will be in demand"
    }
]

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome to the AI Service!"}

@app.get("/posts", tags=["Endpoints ~ HTML"])
def get_posts():
    return {"posts": BLOG_POST}

""" INFO:
  Utilizando Plantillas para construir HTML que se mostrará en el Navegador desde Python 
  esto es a Manera de Ejemplo Ya que el Verdadero Frontend estará hecho en Angular
  y recibirá las respuestas desde el Backend realizado en NestJS. 
"""
@app.get("/posts/template", tags=["Endpoints ~ HTML"])
def get_home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(request, "home.html", { "posts": posts, "title": "Home" })


@app.get("/posts/html", response_class=HTMLResponse, include_in_schema=False)
def get_posts_html():
    return f'<h1>{BLOG_POST[0]['title']}</h1>'

@app.get("/params", tags=["Endpoints ~ HTML"])
def get_posts_Query_params(query: str | None = Query(default=None, description="Query string to search posts"), limit: int = 5):
    posts = BLOG_POST
    if query:
        posts = [post for post in posts if query.lower() in post["title"].lower()]
    return {"posts": posts[:limit]}


@app.get("/params/{id}", tags=["Endpoints ~ HTML"])
def get_post_param(id: int | None = None, include_content: bool | None = Query(default=True, description="Query string to see posts")):
    for post in BLOG_POST:
        if post["id"] == id and (include_content):
            return {"post": post}
        else:
            return {"post": {"id": post["id"], "title": post["title"]}}
    return {"error": "Post not found"}

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


@app.get("/posts/{post_id}", tags=["Endpoints ~ HTML"])
def get_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post).where(models.models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    title = post.title[:50]
    return templates.TemplateResponse(request, "post.html", { "post": post, "title": title })

''' Hasta aquí llega el codigo HTML de pruebas.'''


# Post Methods for FastAPI que responderan a NestJS que al final le Mandará las respuestas al Frontend en Angular.
@app.get("/api/posts", response_model=list[PostResponse], tags=["Endpoins ~ Posts"])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post))
    posts = result.scalars().all()
    return posts

@app.get("/api/posts/{id}", response_model=PostResponse, tags=["Endpoins ~ Posts"])
def get_post(id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post).where(models.models.Post.id == id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED, tags=["Endpoins ~ Posts"])
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.User).where(models.models.User.id == post.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")
    
    new_post = models.models.Post(title=post.title, content=post.content, user_id=post.user_id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


""" @app.put("/api/posts/{id}", response_model=BlogPost, tags=["Endpoins ~ Posts"], status_code=status.HTTP_200_OK)
def update_post_full(id: int, item: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == id:
            if "title" in item:
                if not isinstance(item["title"], str):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title must be a string")
                if "content" in item:
                    if not isinstance(item["content"], str):
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content must be a string")
                    post["content"] = item["content"]
                post["title"] = item["title"]
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") """

@app.put("/api/posts/{id}", response_model=BlogPost, status_code=status.HTTP_200_OK, tags=["Endpoins ~ Posts"])
def update_post_full(id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post).where(models.models.Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.models.User).where(models.models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")    
                    
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post


@app.patch("/api/posts/{id}", response_model=BlogPost, status_code=status.HTTP_200_OK, tags=["Endpoins ~ Posts"])
def update_post_partial(id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.Post).where(models.models.Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    update_data = post_data.model_dump(exclude_unset=True) # Se validan los campos a ser Actualizados, devolviendo un Diccionario con los vlores a cambiar.
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post


@app.delete("/api/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Endpoins ~ Posts"])
def delete_post(id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == id:
            BLOG_POST.pop(index)
            return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# Simulación de análisis de facturas con IA con NestJS y Angular
@app.post("/api/analyze", include_in_schema=False)
def analyze(data: AnalysisRequest):
    # Simulación IA
    score = len(str(data.invoice)) * 0.1
    return {
        "risk_score": round(score, 2), # Redondeamos para que se vea limpio en Angular
        "decision": "approve" if score < 5 else "reject",
        "invoice_processed": data.invoice
    }


# Enpoints for the Users:
@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["Endpoins ~ Users"])
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.User).where(models.models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")
    
    return user


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse], tags=["Endpoins ~ Users"])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.User).where(models.models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")
    
    result = db.execute(select(models.models.Post).where(models.models.Post.user_id == user_id))
    posts = result.scalars().all()

    return posts


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Endpoins ~ Users"])
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.models.User).where(models.models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist")
    

    result = db.execute(select(models.models.User).where(models.models.User.email == user.email))
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    new_user = models.models.User(username=user.username, email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
