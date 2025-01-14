async function askMagicAI() {
    const prompt = document.getElementById("prompt").value;
    const responseElement = document.getElementById("response");

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();
        responseElement.textContent = data.response || data.error;
    } catch (error) {
        responseElement.textContent = "Error: " + error.message;
    }
}