import { updateDeviceCount } from './deviceCount.js';
import { updateStatusBadge } from './helpers/updateStatusBadge.js';

export function initializeStatusToggles() {
    const statusToggles = document.querySelectorAll('.status-toggle');

    statusToggles.forEach(toggle => {
        toggle.addEventListener('click', async function() {
            const deviceId = this.dataset.deviceId;
            const currentStatus = this.dataset.status;
            const newStatus = currentStatus === 'on' ? 'off' : 'on';
            
            try {
                const response = await fetch(`/appliances/${deviceId}/toggle/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ status: newStatus })
                });
                
                if (response.ok) {
                    this.dataset.status = newStatus;
                    const toggleBg = this.querySelector('.status-toggle-bg');
                    const toggleHandle = this.querySelector('.status-toggle-handle');
                    
                    if (newStatus === 'on') {
                        toggleBg.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                        toggleBg.classList.add('bg-green-500');
                        toggleHandle.classList.add('translate-x-6');
                    } else {
                        toggleBg.classList.remove('bg-green-500');
                        toggleBg.classList.add('bg-gray-300', 'dark:bg-gray-600');
                        toggleHandle.classList.remove('translate-x-6');
                    }
                    
                    updateStatusBadge(deviceId, newStatus);
                    updateDeviceCount(newStatus);
                } else {
                    console.error('Failed to toggle device status');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
}