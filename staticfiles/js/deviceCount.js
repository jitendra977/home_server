export function updateDeviceCount(newStatus) {
    const activeCount = document.getElementById('activeCount');
    const inactiveCount = document.getElementById('inactiveCount');
    
    if (newStatus === 'on') {
        activeCount.textContent = parseInt(activeCount.textContent) + 1;
        inactiveCount.textContent = parseInt(inactiveCount.textContent) - 1;
    } else {
        activeCount.textContent = parseInt(activeCount.textContent) - 1;
        inactiveCount.textContent = parseInt(inactiveCount.textContent) + 1;
    }
}