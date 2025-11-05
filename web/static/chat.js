const API_URL = 'https://ai-chatbot-2-osma.onrender.com/api/chat'; // your Render backend

const input = document.getElementById('input');
const sendButton = document.getElementById('send');
const messagesContainer = document.querySelector('.messages');

// send message on Enter key
input.addEventListener('keypress', function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendButton.addEventListener('click', sendMessage);

function appendMessage(sender, text) {
  const msg = document.createElement('div');
  msg.classList.add('msg', sender);
  msg.innerText = text;
  messagesContainer.appendChild(msg);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  appendMessage('user', message);
  input.value = '';

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    appendMessage('bot', data.reply || 'No response.');
  } catch (err) {
    console.error(err);
    appendMessage('bot', 'Error: Unable to connect to server.');
  }
}
