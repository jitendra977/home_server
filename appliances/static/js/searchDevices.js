
// searchDevices.js
export default function initializeSearch() {
    const searchInput = document.getElementById('deviceSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const deviceCards = document.querySelectorAll('.device-card');

            deviceCards.forEach(card => {
                const name = card.querySelector('h4').textContent.toLowerCase();
                const location = card.querySelector('p').textContent.toLowerCase();
                card.style.display = (name.includes(searchTerm) || location.includes(searchTerm)) ? 'block' : 'none';
            });
        });
    }
}