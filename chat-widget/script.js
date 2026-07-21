document.addEventListener('DOMContentLoaded', () => {
    const chatWidgetBtn = document.getElementById('chatWidgetBtn');
    const chatWindow = document.getElementById('chatWindow');
    const closeChatBtn = document.getElementById('closeChatBtn');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const headerChatBtn = document.querySelector('.header-chat-btn');

    // Toggle Chat Window
    const toggleChat = () => {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            chatInput.focus();
        }
    };

    chatWidgetBtn.addEventListener('click', toggleChat);
    headerChatBtn.addEventListener('click', toggleChat);
    closeChatBtn.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    // Handle Sending Messages
    const sendMessage = () => {
        const text = chatInput.value.trim();
        if (text === '') return;

        // Add User Message
        addMessage(text, 'user-message');
        chatInput.value = '';

        // Simulate AI Response
        setTimeout(() => {
            const responses = [
                "I'm here to help you build great software!",
                "That's a fantastic question.",
                "Let's elevate your startup to the next level.",
                "I can definitely assist you with that.",
                "Would you like to schedule a quick call to discuss?",
                "Our AI capabilities can automate this for you."
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse, 'ai-message');
        }, 800);
    };

    const addMessage = (text, className) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Event Listeners for Send
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
