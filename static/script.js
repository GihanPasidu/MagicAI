async function askMagicAI() {
    const prompt = document.getElementById("prompt").value;
    const chatMessages = document.getElementById("chatMessages");
    const askButton = document.getElementById("askButton");

    if (!prompt.trim()) {
        alert("Please enter a question");
        return;
    }

    // Add user message
    addMessage(prompt, 'user');

    // Disable button and show loading
    askButton.disabled = true;
    const loadingMessage = addMessage('Thinking...', 'bot loading');

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Replace loading message with response
        loadingMessage.textContent = data.response;
        loadingMessage.classList.remove('loading');
    } catch (error) {
        loadingMessage.textContent = `Error: ${error.message}`;
        loadingMessage.classList.add('error');
    } finally {
        askButton.disabled = false;
        document.getElementById("prompt").value = "";
        scrollToBottom();
    }
}

function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `message ${type}`;
    message.textContent = text;
    chatMessages.appendChild(message);
    return message;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function fetchModelInfo() {
    try {
        const response = await fetch('/model-info');
        const data = await response.json();
        document.getElementById("modelName").textContent = data.name;
        document.getElementById("modelVersion").textContent = data.version;
        document.getElementById("modelDescription").textContent = data.description;
    } catch (error) {
        console.error("Error fetching model info:", error);
    }
}

// Event listeners
document.getElementById("prompt").addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        askMagicAI();
    }
});

document.addEventListener("DOMContentLoaded", fetchModelInfo);