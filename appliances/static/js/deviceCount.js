
// deviceCount.js
export default function updateDeviceCounts() {
    const active = document.querySelectorAll('.status-toggle[data-status="on"]').length;
    const inactive = document.querySelectorAll('.status-toggle[data-status="off"]').length;

    const activeCount = document.getElementById('activeCount');
    const inactiveCount = document.getElementById('inactiveCount');

    if (activeCount) activeCount.textContent = active;
    if (inactiveCount) inactiveCount.textContent = inactive;
}
