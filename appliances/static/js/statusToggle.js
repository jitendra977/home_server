// js/statusToggle.js
import { showNotification } from './helpers/showErrorNotification.js';
import { updateStatusBadge } from './helpers/updateStatusBadge.js';

export async function updateDeviceStatus(deviceId, toggleButton) {
    const currentStatus = toggleButton.dataset.status;
    const newStatus = currentStatus === 'on' ? 'off' : 'on';
    
    try {
        const response = await fetch(`/control/toggle/${deviceId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                status: newStatus === 'on'
            })
        });

        if (response.ok) {
            const data = await response.json();
            
            // Update toggle button state
            toggleButton.dataset.status = newStatus;
            
            // Update toggle appearance
            const toggleBg = toggleButton.querySelector('.status-toggle-bg');
            const toggleHandle = toggleButton.querySelector('.status-toggle-handle');
            
            if (newStatus === 'on') {
                toggleBg.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                toggleBg.classList.add('bg-green-500');
                toggleHandle.classList.add('translate-x-6');
            } else {
                toggleBg.classList.remove('bg-green-500');
                toggleBg.classList.add('bg-gray-300', 'dark:bg-gray-600');
                toggleHandle.classList.remove('translate-x-6');
            }
            
            // Update status badges
            updateStatusBadge(deviceId, newStatus);
            
            // Show success message
            showNotification('Device status updated successfully', 'success');
            
        } else {
            throw new Error('Failed to toggle device status');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to update device status', 'error');
        // Revert toggle state
        toggleButton.querySelector('.status-toggle-handle').classList.toggle('translate-x-6');
    }
}

export function initStatusToggles() {
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const deviceId = this.dataset.deviceId;
            // Add loading state
            this.classList.add('opacity-50', 'pointer-events-none');
            
            updateDeviceStatus(deviceId, this).finally(() => {
                // Remove loading state
                this.classList.remove('opacity-50', 'pointer-events-none');
            });
        });
    });
}