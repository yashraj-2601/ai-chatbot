AI-Powered Chatbot


Minimal retrieval-style chatbot using a public conversation dataset. Good for publishing on GitHub as a demonstration project.


**Dataset (clickable):** https://github.com/FareedKhan-dev/AI-Chatbot-Conversation-Dataset


### Features
- FastAPI backend that loads a conversation dataset and builds a TF-IDF retriever.
- Static frontend with black / blue / purple theme.
- Press **Enter** to send (Shift+Enter for newline).
- Lightweight. No large models required.


### Run locally
1. Clone this repo.
2. Create venv and install deps:
```bash
python -m venv venv
source venv/bin/activate # macOS / Linux
venv\Scripts\activate # Windows
pip install -r requirements.txt