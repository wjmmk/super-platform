from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel

app = FastAPI(title="AI Service", version="1.0")

class BlogPost(BaseModel):
    id: int
    title: str
    content: str

class AnalysisRequest(BaseModel):
    invoice: str | int

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    is_offer: bool | None = None

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

@app.get("/")
def home():
    return {"message": "Welcome to the AI Service!"}

@app.get("/posts")
def get_posts():
    return {"posts": BLOG_POST}

@app.get("/params")
def get_posts_Query_params(query: str | None = Query(default=None, description="Query string to search posts"), limit: int = 5):
    posts = BLOG_POST
    if query:
        posts = [post for post in posts if query.lower() in post["title"].lower()]
    return {"posts": posts[:limit]}

@app.get("/params/{id}")
def get_post_param(id: int | None = None, include_content: bool | None = Query(default=True, description="Query string to see posts")):
    for post in BLOG_POST:
        if post["id"] == id and (include_content):
            return {"post": post}
        else:
            return {"post": {"id": post["id"], "title": post["title"]}}
    return {"error": "Post not found"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{id}", response_model=BlogPost)
def read_item(id: int | None = None):
    post = next((post for post in BLOG_POST if post["id"] == id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post["id"], "title": post["title"], "content": post["content"]}


# Post Methods for FastAPI.
@app.post("/posts")
def create_post(post: dict = Body(...)):
    if "title" not in post or "content" not in post:
        raise HTTPException(status_code=400, detail="Title and content are required")
    
    if not isinstance(post["title"], str) or not isinstance(post["content"], str):
        raise HTTPException(status_code=400, detail="Title and content must be strings")
    
    new_id = max(post["id"] for post in BLOG_POST) + 1
    new_post = {"id": new_id, **post}
    BLOG_POST.append(new_post)
    return {"message": "Post created successfully", "post": new_post}


@app.put("/posts/{id}", response_model=BlogPost)
def update_item(id: int, item: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == id:
            if "title" in item:
                if not isinstance(item["title"], str):
                    raise HTTPException(status_code=400, detail="Title must be a string")
                if "content" in item:
                    if not isinstance(item["content"], str):
                        raise HTTPException(status_code=400, detail="Content must be a string")
                    post["content"] = item["content"]
                post["title"] = item["title"]
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{id}", status_code=204)
def delete_item(id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == id:
            BLOG_POST.pop(index)
            return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")


# Simulación de análisis de facturas con IA con NestJS y Angular
@app.post("/analyze")
def analyze(data: AnalysisRequest):
    # Simulación IA
    score = len(str(data.invoice)) * 0.1
    return {
        "risk_score": round(score, 2), # Redondeamos para que se vea limpio en Angular
        "decision": "approve" if score < 5 else "reject",
        "invoice_processed": data.invoice
    }

