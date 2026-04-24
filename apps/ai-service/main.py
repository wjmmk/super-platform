from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, status, Query, Body, Request, Depends
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from schemas import AnalysisRequest, BlogPost

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models.models
from database import engine, get_db
from routers import posts, users


""" # Creacion de la DB and Tables.
Base.metadata.create_all(bind=engine) Esto es para la creacion de tablas Sincronas """

# Creacion de DB & tablas Asincronamente para la Carga Diferida entre Consultas a da DBs.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan, title="AI Service", version="1.0")

# Routes for Media Files.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Permite usar plantillas HTML desde FastAPI.
templates = Jinja2Templates(directory="templates")

# Enrutadores de APIs implementados.
app.include_router(users.router, prefix="/api/users", tags=["Endpoint ~ Users"])
app.include_router(posts.router, prefix="/api/posts", tags=["Endpoints ~ Posts"])


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
async def get_home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).options(selectinload(models.models.Post.author)))
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
async def get_post(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).options(selectinload(models.models.Post.author)).where(models.models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    title = post.title[:50]
    return templates.TemplateResponse(request, "post.html", { "post": post, "title": title })


@app.put("/posts/{id}", response_model=BlogPost, tags=["Endpoints ~ HTML"], status_code=status.HTTP_200_OK)
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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# Simulación de análisis de facturas con IA con NestJS y Angular
@app.post("/api/analyze", include_in_schema=False)
async def analyze(data: AnalysisRequest):
    # Simulación IA
    score = len(str(data.invoice)) * 0.1
    return {
        "risk_score": round(score, 2), # Redondeamos para que se vea limpio en Angular
        "decision": "routerrove" if score < 5 else "reject",
        "invoice_processed": data.invoice
    }


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )