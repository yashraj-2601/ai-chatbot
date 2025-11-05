from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = FastAPI(title="AI Chatbot — TF-IDF retriever")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "conversations.json")


class ChatRequest(BaseModel):
    message: str


# globals
_vectorizer = None
_matrix = None
_responses = []
_threshold = 0.20  # slightly lower to catch more matches


def load_data(path: str = DATA_PATH):
    """Load Q/A pairs and build TF-IDF index."""
    global _vectorizer, _matrix, _responses

    if not os.path.exists(path):
        print("Data file not found at", path)
        _vectorizer = None
        _matrix = None
        _responses = []
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            items = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in", path)
            _vectorizer = None
            _matrix = None
            _responses = []
            return

    pairs = []
    for it in items or []:
        if isinstance(it, dict):
            q = it.get("question") or it.get("q") or it.get("input") or it.get("pattern")
            a = it.get("answer") or it.get("a") or it.get("response") or it.get("reply")
            if q and a:
                pairs.append((q.strip(), a.strip()))

    if not pairs:
        print("No valid QA pairs found in data file")
        _vectorizer = None
        _matrix = None
        _responses = []
        return

    queries, answers = zip(*pairs)
    _responses = list(answers)
    _vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    _matrix = _vectorizer.fit_transform(queries)
    print("Loaded", len(queries), "pairs")


@app.on_event("startup")
def startup_event():
    load_data()


@app.get("/health")
def health():
    ok = _vectorizer is not None and _matrix is not None and len(_responses) > 0
    return {"ok": ok, "pairs": len(_responses)}


@app.post("/api/reload")
def reload_data():
    load_data()
    return {"status": "reloaded", "pairs": len(_responses)}


@app.post("/api/chat")
def chat(req: ChatRequest):
    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="empty message")

    low = msg.lower().strip()

    # Rule-based intents for common phrases
    rules = [
        (("hi", "hello", "hey"), "Hello. How can I help you today?"),
        (("how are you", "how r u", "how are you doing"), "I don’t have feelings, but I’m working."),
        (("your name", "what is your name", "who are you"), "I’m an AI chatbot built with FastAPI and a simple retriever."),
        (("what can you do", "capabilities", "features"), "I answer basic questions from my dataset and simple rule-based intents."),
        (
            ("tell me about this project", "about this project", "project details"),
            "Frontend on GitHub Pages, backend on Render. Retrieval uses TF-IDF over a small Q/A set.",
        ),
        (("thank you", "thanks", "ty"), "You're welcome."),
        (("bye", "goodbye", "see you"), "Goodbye. Have a nice day."),
    ]
    for keys, reply in rules:
        if any(k in low for k in keys):
            return {"reply": reply}

    # Retrieval fallback
    global _vectorizer, _matrix, _responses
    if _vectorizer is None or _matrix is None:
        return {"reply": "Dataset not loaded. Add data/conversations.json and redeploy or call /api/reload."}

    v = _vectorizer.transform([msg])
    sims = linear_kernel(v, _matrix).flatten()
    idx = sims.argmax()
    best = sims[idx]
    if best >= _threshold:
        return {"reply": _responses[idx], "score": float(best)}

    return {"reply": "I don't know that yet. Try rephrasing or add more Q/A pairs to the dataset."}
