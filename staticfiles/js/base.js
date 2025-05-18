document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const voiceBtn = document.getElementById('voiceInput');

    // Scroll chat to bottom
    function scrollChat() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Handle chat submit (demo only, replace with AJAX for real bot)
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;
        // Append user message
        const userMsg = document.createElement('div');
        userMsg.className = 'user-msg';
        userMsg.innerHTML = text;
        chatBox.appendChild(userMsg);
        userInput.value = '';
        scrollChat();

        // Simulate bot reply
        setTimeout(() => {
            const botMsg = document.createElement('div');
            botMsg.className = 'bot-msg';
            botMsg.innerHTML = `<strong>FixIT:</strong> That's a great question! (This is a demo reply.)`;
            chatBox.appendChild(botMsg);
            scrollChat();
        }, 800);
    });

    // Voice input animation (demo only)
    voiceBtn.addEventListener('click', function() {
        voiceBtn.classList.add('active');
        voiceBtn.innerText = '🎙️ Listening...';
        setTimeout(() => {
            voiceBtn.classList.remove('active');
            voiceBtn.innerText = '🎙️ Speak Instead';
        }, 2000);
    });
});
