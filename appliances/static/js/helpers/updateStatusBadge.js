// js/helpers/updateStatusBadge.js
export function updateStatusBadge(deviceId, newStatus) {
    const statusBadges = document.querySelectorAll(`[data-device-id="${deviceId}"] .status-badge`);
    statusBadges.forEach(badge => {
        const icon = badge.querySelector('i');
        icon.classList.remove('fa-power-off', 'fa-circle');
        icon.classList.add(newStatus === 'on' ? 'fa-power-off' : 'fa-circle');
        
        badge.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
            newStatus === 'on' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        }`;
        badge.querySelector('span').textContent = newStatus === 'on' ? 'ONLINE' : 'OFFLINE';
    });
    
    // Update counters in header stats
    const activeCount = document.getElementById('activeCount');
    const inactiveCount = document.getElementById('inactiveCount');
    
    if (activeCount && inactiveCount) {
        if (newStatus === 'on') {
            activeCount.textContent = parseInt(activeCount.textContent) + 1;
            inactiveCount.textContent = Math.max(0, parseInt(inactiveCount.textContent) - 1);
        } else {
            activeCount.textContent = Math.max(0, parseInt(activeCount.textContent) - 1);
            inactiveCount.textContent = parseInt(inactiveCount.textContent) + 1;
        }
    }
    
    // Update room statistics
    const roomId = document.querySelector(`[data-device-id="${deviceId}"]`).dataset.roomId;
    const activeRoomsCount = document.getElementById('activeRooms');
    
    // Check if this was the last active device in the room
    const roomDevices = document.querySelectorAll(`[data-room-id="${roomId}"] .status-toggle`);
    const hasActiveDevices = Array.from(roomDevices).some(device => 
        device.dataset.status === 'on' && device.dataset.deviceId !== deviceId
    );
    
    if (activeRoomsCount) {
        const currentActiveRooms = parseInt(activeRoomsCount.textContent);
        if (newStatus === 'on' && !hasActiveDevices) {
            activeRoomsCount.textContent = currentActiveRooms + 1;
        } else if (newStatus === 'off' && !hasActiveDevices) {
            activeRoomsCount.textContent = Math.max(0, currentActiveRooms - 1);
        }
    }
}