export function updateStatusBadge(deviceId, newStatus) {
    const statusBadge = document.querySelector(`.device-card[data-device-id="${deviceId}"] .status-badge`);
    if (statusBadge) {
        statusBadge.textContent = newStatus === 'on' ? 'ONLINE' : 'OFFLINE';
        statusBadge.className = newStatus === 'on' 
            ? 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
            : 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
}