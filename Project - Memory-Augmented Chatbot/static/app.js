const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// generate a random session id for memory
const userId = "user_" + Math.random().toString(36).substr(2, 9);

function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // hacky way to handle newlines
    contentDiv.innerHTML = text.replace(/\n/g, '<br>');
    
    msgDiv.appendChild(contentDiv);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot-message typing-msg';
    msgDiv.id = 'typingIndicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    
    msgDiv.appendChild(contentDiv);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // clear input and disable btn
    userInput.value = '';
    sendBtn.disabled = true;

    // show user msg
    addMessage(text, true);
    
    // show typing animation
    showTyping();

    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                user_id: userId
            })
        });

        const data = await response.json();
        removeTyping();
        
        if (response.ok) {
            addMessage(data.response);
        } else {
            console.error("api error:", data);
            addMessage("Oops, something broke on the server! Check console.");
        }
    } catch (err) {
        console.error("fetch failed:", err);
        removeTyping();
        addMessage("Network error. Is the server running?");
    }

    sendBtn.disabled = false;
    userInput.focus();
}

// event listeners
sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
