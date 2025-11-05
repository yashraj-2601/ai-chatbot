document.addEventListener('DOMContentLoaded', () => {
  const API_URL = 'https://ai-chatbot-2-osma.onrender.com/api/chat'; // Render API

  const input = document.getElementById('input');
  const sendButton = document.getElementById('send');
  const messages = document.getElementById('messages');
  const form = document.getElementById('composer');

  function append(text, who = 'bot') {
    const d = document.createElement('div');
    d.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
    d.textContent = text;
    messages.appendChild(d);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;
    append(message, 'user');
    input.value = '';

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      append(data.reply || 'No response.');
    } catch (e) {
      append('Error connecting to server. Try again.');
      console.error(e);
    }
  }

  // Enter to send. Shift+Enter = newline.
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendButton.addEventListener('click', (e) => {
    e.preventDefault();
    sendMessage();
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage();
  });

  // starter msg
  append('Hi. Ask me something like "hello" or "bye".');
});

