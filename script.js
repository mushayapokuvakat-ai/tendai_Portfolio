document.addEventListener('DOMContentLoaded', () => {

    // 1. Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            const isOpened = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isOpened);
            navLinks.classList.toggle('active');

            // Add/Remove class to body to prevent scroll when menu is open
            document.body.style.overflow = isOpened ? 'auto' : 'hidden';
        });
    }

    // Close menu when clicking a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            menuToggle.setAttribute('aria-expanded', 'false');
            navLinks.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    });

    // 2. Skill Bar Animation (Intersection Observer)
    const skillBars = document.querySelectorAll('.progress-bar');

    const observerOptions = {
        threshold: 0.5
    };

    const skillObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-width');
                bar.style.width = width;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    skillBars.forEach(bar => skillObserver.observe(bar));

    // 3. Contact Form Submission (Simulated)
    const contactForm = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const submitBtn = contactForm.querySelector('button');
            const originalText = submitBtn.textContent;

            // Disable button and show sending state
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            // Simulate API request
            setTimeout(() => {
                const name = document.getElementById('name').value;
                formStatus.textContent = `Message sent successfully! Thanks, ${name}.`;
                formStatus.style.color = '#00CC00';

                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;

                // Clear status after 5 seconds
                setTimeout(() => {
                    formStatus.textContent = '';
                }, 5000);
            }, 1500);
        });
    }

    // 5. AI Chat Toggle & Logic
    const openChatBtn = document.getElementById('open-chat');
    const closeChatBtn = document.getElementById('close-chat');
    const chatWidget = document.getElementById('ai-chat-widget');
    const chatForm = document.getElementById('chat-input-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    const addMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    if (openChatBtn && closeChatBtn && chatWidget) {
        openChatBtn.addEventListener('click', () => {
            chatWidget.classList.add('active');
            openChatBtn.style.display = 'none';
        });

        closeChatBtn.addEventListener('click', () => {
            chatWidget.classList.remove('active');
            openChatBtn.style.display = 'block';
        });
    }

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            chatInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                if (response.ok) {
                    const data = await response.json();
                    addMessage(data.response, 'ai');
                } else {
                    addMessage("I'm having trouble connecting to Tendai's server right now. Check if the backend is running!", 'ai');
                }
            } catch (error) {
                console.error('Chat error:', error);
                addMessage("Oops! I can't reach Tendai's server right now. It might be waking up—please try again in a few seconds.", 'ai');
            }
        });
    }
});
