function sendMessage() {
    const inputElement = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");
    const userMessage = inputElement.value.trim();

    if (userMessage === "") return;

    // Append user message
    const userMessageElement = document.createElement("div");
    userMessageElement.className = "message user";
    userMessageElement.textContent = userMessage;
    chatBox.appendChild(userMessageElement);

    // Send message to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        const botMessageElement = document.createElement("div");
        botMessageElement.className = "message bot";
        botMessageElement.textContent = data.reply;
        chatBox.appendChild(botMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll
    });

    inputElement.value = "";
}
