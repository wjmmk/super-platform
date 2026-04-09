# apps/ai-service/main.py

from fastapi import FastAPI

app = FastAPI(title="AI Service", version="1.0")

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

@app.post("/analyze")
def analyze(data: dict):
    # Simulación IA
    score = len(str(data)) * 0.1
    return {
        "risk_score": score,
        "decision": "approve" if score < 5 else "reject"
    }