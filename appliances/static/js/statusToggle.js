// statusToggle.js
import updateDeviceCounts from './deviceCount.js';
import updateStatusBadge from './helpers/updateStatusBadge.js';
import showErrorNotification from './helpers/showErrorNotification.js';

export default function initializeStatusToggles() {
    const statusToggles = document.querySelectorAll('.status-toggle');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }

    statusToggles.forEach(toggle => {
        toggle.addEventListener('click', async function(e) {
            e.preventDefault();

            const deviceId = this.dataset.deviceId;
            const isCurrentlyOn = this.dataset.status === 'on';
            const newStatus = isCurrentlyOn ? 'off' : 'on';
            const bg = this.querySelector('.status-toggle-bg');
            const handle = this.querySelector('.status-toggle-handle');
            const deviceCard = this.closest('.device-card');
            const tableRow = this.closest('tr');
            const statusBadge = deviceCard ?
                deviceCard.querySelector('.status-badge') :
                tableRow ? tableRow.querySelector('.status-badge') : null;

            if (handle) handle.innerHTML = '<i class="fas fa-spinner fa-spin text-xs"></i>';

            try {
                const response = await fetch(`/control/toggle/${deviceId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'Accept': 'application/json'
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ status: newStatus === 'on', device_id: deviceId })
                });

                const data = await response.json();

                if (data.success) {
                    this.dataset.status = newStatus;
                    this.setAttribute('data-status', newStatus);

                    if (bg && handle) {
                        if (newStatus === 'on') {
                            bg.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                            bg.classList.add('bg-green-500');
                            handle.classList.add('translate-x-6');
                        } else {
                            bg.classList.remove('bg-green-500');
                            bg.classList.add('bg-gray-300', 'dark:bg-gray-600');
                            handle.classList.remove('translate-x-6');
                        }
                        handle.innerHTML = '';
                    }

                    if (statusBadge) {
                        updateStatusBadge(statusBadge, newStatus);
                    }

                    updateDeviceCounts();
                } else {
                    throw new Error(data.error || 'Failed to update device status');
                }
            } catch (error) {
                console.error('Error toggling device status:', error);
                this.dataset.status = isCurrentlyOn ? 'on' : 'off';
                if (handle) handle.innerHTML = '';
                showErrorNotification(error.message);
            }
        });
    });

    updateDeviceCounts();
}
