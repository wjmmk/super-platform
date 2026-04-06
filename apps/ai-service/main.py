# apps/ai-service/main.py

from fastapi import FastAPI

app = FastAPI()

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