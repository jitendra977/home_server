// helpers/updateStatusBadge.js
export default function updateStatusBadge(badge, status) {
    if (!badge) return;

    const icon = badge.querySelector('i');
    const text = badge.querySelector('span') || badge.lastChild;

    if (status === 'on') {
        badge.classList.remove('bg-gray-200', 'text-gray-800', 'dark:bg-gray-700', 'dark:text-gray-300');
        badge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900/50', 'dark:text-green-300');
        if (icon) {
            icon.classList.remove('fa-circle');
            icon.classList.add('fa-power-off');
        }
        if (text) text.textContent = 'ONLINE';
    } else {
        badge.classList.remove('bg-green-100', 'text-green-800', 'dark:bg-green-900/50', 'dark:text-green-300');
        badge.classList.add('bg-gray-200', 'text-gray-800', 'dark:bg-gray-700', 'dark:text-gray-300');
        if (icon) {
            icon.classList.remove('fa-power-off');
            icon.classList.add('fa-circle');
        }
        if (text) text.textContent = 'OFFLINE';
    }
}