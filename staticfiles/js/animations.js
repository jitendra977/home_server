
// animations.js
export default function initializeAnimations() {
    const cards = document.querySelectorAll('.device-card');
    cards.forEach((card, i) => {
        card.style.animationDelay = `${i * 0.1}s`;
        card.classList.add('animate-fade-in');
    });
}