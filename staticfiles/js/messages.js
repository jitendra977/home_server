// Auto-hide messages
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert-message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});