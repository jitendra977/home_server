export function showErrorNotification(message) {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('error-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'error-notification';
        notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 hidden';
        document.body.appendChild(notification);
    }

    // Set message and show
    notification.textContent = message;
    notification.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}