
// helpers/showErrorNotification.js
export default function showErrorNotification(message) {
    const note = document.createElement('div');
    note.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    note.innerHTML = `<div class="flex items-center space-x-2"><i class="fas fa-exclamation-circle"></i><span>${message}</span></div>`;
    document.body.appendChild(note);
    setTimeout(() => {
        note.classList.add('animate-fade-out');
        setTimeout(() => note.remove(), 300);
    }, 3000);
}
