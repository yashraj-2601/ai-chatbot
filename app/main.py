from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = FastAPI(title='AI Chatbot — TF-IDF retriever')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'conversations.json')

class ChatRequest(BaseModel):
    message: str

_vectorizer = None
_matrix = None
_responses = []
_threshold = 0.25  # similarity threshold


def load_data(path=DATA_PATH):
    global _vectorizer, _matrix, _responses
    if not os.path.exists(path):
        print('Data file not found at', path)
        _responses = []
        _vectorizer = None
        _matrix = None
        return
    with open(path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    pairs = []
    for it in items:
        if isinstance(it, dict):
            q = it.get('question') or it.get('q') or it.get('input') or it.get('pattern')
            a = it.get('answer') or it.get('a') or it.get('response') or it.get('reply')
            if q and a:
                pairs.append((q.strip(), a.strip()))
    if not pairs:
        print('No valid QA pairs found in data file')
        _responses = []
        _vectorizer = None
        _matrix = None
        return
    queries, answers = zip(*pairs)
    _responses = list(answers)
    _vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = _vectorizer.fit_transform(queries)
    _matrix = X
    print('Loaded', len(queries), 'pairs')


@app.on_event('startup')
def startup_event():
    load_data()


@app.post('/api/chat')
def chat(req: ChatRequest):
    msg = req.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail='empty message')

    low = msg.lower()
    if any(g in low for g in ('hi', 'hello', 'hey')):
        return {'reply': 'Hello. How can I help you today?'}
    if 'thank' in low:
        return {'reply': "You're welcome."}
    if 'bye' in low or 'goodbye' in low:
        return {'reply': 'Goodbye. Have a nice day.'}

    global _vectorizer, _matrix, _responses
    if _vectorizer is None or _matrix is None:
        return {'reply': "Dataset not loaded. Add data/conversations.json."}
    v = _vectorizer.transform([msg])
    sims = linear_kernel(v, _matrix).flatten()
    idx = sims.argmax()
    best = sims[idx]
    if best >= _threshold:
        return {'reply': _responses[idx], 'score': float(best)}
    return {'reply': "I don't know that yet. Try rephrasing or update the dataset."}
