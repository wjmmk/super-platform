# apps/ai-service/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Service", version="1.0")

class BlogPost(BaseModel):
    id: int
    title: str
    content: str

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    is_offer: bool | None = None

BLOG_POST = [
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{id}", response_model=BlogPost)
def read_item(id: int, q: str | None = None):
    post = next((post for post in BLOG_POST if post["id"] == id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post["id"], "title": post["title"], "content": post["content"]}

@app.post("/analyze")
def analyze(data: dict):
    # Simulación IA
    score = len(str(data)) * 0.1
    return {
        "risk_score": score,
        "decision": "approve" if score < 5 else "reject"
    }

@app.put("/items/{item_id}", response_model=BlogPost)
def update_item(item_id: int, item: BlogPost):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == item_id:
            # 2. Reemplazamos el contenido en esa posición
            # .model_dump() convierte el objeto de Pydantic en un diccionario de Python
            BLOG_POST[index] = item.model_dump()
            return BLOG_POST[index]
    raise HTTPException(status_code=404, detail="Post not found")