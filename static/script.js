async function askMagicAI() {
    const prompt = document.getElementById("prompt").value;
    const chatMessages = document.getElementById("chatMessages");
    const askButton = document.getElementById("askButton");

    if (!prompt.trim()) return;

    // Display user message
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.textContent = prompt;
    chatMessages.appendChild(userMessage);

    // Clear input
    document.getElementById("prompt").value = "";

    // Display loading message
    const loadingMessage = document.createElement("div");
    loadingMessage.className = "message bot";
    loadingMessage.textContent = "Loading...";
    chatMessages.appendChild(loadingMessage);

    askButton.disabled = true;

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();
        loadingMessage.textContent = data.response_text || data.error;
    } catch (error) {
        loadingMessage.textContent = "Error: " + error.message;
    } finally {
        askButton.disabled = false;
    }

    // Scroll to the bottom of the chat
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

document.addEventListener("DOMContentLoaded", fetchModelInfo);