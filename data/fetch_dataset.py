import os
import requests
import json
from urllib.parse import urljoin

OUT = os.path.join(os.path.dirname(__file__), 'conversations.json')
BASE = 'https://raw.githubusercontent.com/FareedKhan-dev/AI-Chatbot-Conversation-Dataset/main/'
CANDIDATES = [
    'conversations.json',
    'dataset.json',
    'intents.json',
    'chatbot_dataset.json',
    'data.json',
]


def try_download():
    for name in CANDIDATES:
        url = urljoin(BASE, name)
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                print('Found', name)
                content = r.text
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        for k in ('conversations', 'intents', 'data', 'pairs'):
                            if k in parsed and isinstance(parsed[k], list):
                                parsed = parsed[k]
                                break
                    pairs = []
                    for item in parsed:
                        if isinstance(item, dict):
                            q = item.get('question') or item.get('q') or item.get('input') or item.get('pattern')
                            a = item.get('answer') or item.get('a') or item.get('response') or item.get('reply')
                            if q and a:
                                pairs.append({'question': q, 'answer': a})
                    if pairs:
                        with open(OUT, 'w', encoding='utf-8') as f:
                            json.dump(pairs, f, ensure_ascii=False, indent=2)
                        print('Saved', OUT)
                        return True
                except Exception as e:
                    print('Failed to parse', name, e)
        except Exception as e:
            print('Request failed', e)
    print('Could not auto-download dataset. Please place it manually at', OUT)
    return False


if __name__ == '__main__':
    try_download()
