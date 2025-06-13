// devices.js
document.addEventListener('DOMContentLoaded', function() {
    initializeViewToggle();
    initializeStatusToggles();
    initializeSearch();
    initializeDeviceForm();
    initializeAnimations();
});

function initializeViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('gridView');
    const tableView = document.getElementById('tableView');

    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const view = this.dataset.view;

            viewButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            if (view === 'grid') {
                gridView.classList.remove('hidden');
                tableView.classList.add('hidden');
            } else {
                gridView.classList.add('hidden');
                tableView.classList.remove('hidden');
            }
        });
    });
}

function initializeStatusToggles() {
    const statusToggles = document.querySelectorAll('.status-toggle');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    statusToggles.forEach(toggle => {
        toggle.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const deviceId = this.dataset.deviceId;
            const isCurrentlyOn = this.dataset.status === 'on';
            const newStatus = isCurrentlyOn ? 'off' : 'on';
            
            // UI elements
            const bg = this.querySelector('.status-toggle-bg');
            const handle = this.querySelector('.status-toggle-handle');
            const statusBadge = this.closest('.device-card')?.querySelector('.inline-flex') || 
                               this.closest('tr')?.querySelector('.inline-flex');
            
            try {
                // Send status update to server
                const response = await fetch(`/appliances/toggle/${deviceId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ status: newStatus === 'on' })
                });

                if (!response.ok) throw new Error('Failed to update status');

                // Update UI only after successful server update
                this.dataset.status = newStatus;
                
                // Update toggle button
                if (newStatus === 'on') {
                    bg.classList.remove('bg-gray-300', 'dark:bg-gray-600');
                    bg.classList.add('bg-green-500');
                    handle.classList.add('translate-x-6');
                } else {
                    bg.classList.remove('bg-green-500');
                    bg.classList.add('bg-gray-300', 'dark:bg-gray-600');
                    handle.classList.remove('translate-x-6');
                }

                // Update status badge
                if (statusBadge) {
                    const icon = statusBadge.querySelector('i');
                    const text = statusBadge.querySelector('span') || statusBadge.lastChild;
                    
                    if (newStatus === 'on') {
                        statusBadge.classList.remove('bg-gray-200', 'text-gray-800', 'dark:bg-gray-700', 'dark:text-gray-300');
                        statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900/50', 'dark:text-green-300');
                        icon.classList.remove('fa-circle');
                        icon.classList.add('fa-power-off');
                        text.textContent = 'ON';
                    } else {
                        statusBadge.classList.remove('bg-green-100', 'text-green-800', 'dark:bg-green-900/50', 'dark:text-green-300');
                        statusBadge.classList.add('bg-gray-200', 'text-gray-800', 'dark:bg-gray-700', 'dark:text-gray-300');
                        icon.classList.remove('fa-power-off');
                        icon.classList.add('fa-circle');
                        text.textContent = 'OFF';
                    }
                }

                // Update device counts
                updateDeviceCounts();

            } catch (error) {
                console.error('Error toggling device status:', error);
                // Revert UI changes if server update fails
                alert('Failed to update device status. Please try again.');
            }
        });
    });

    updateDeviceCounts();
}

function updateDeviceCounts() {
    const activeDevices = document.querySelectorAll('.status-toggle[data-status="on"]').length;
    const inactiveDevices = document.querySelectorAll('.status-toggle[data-status="off"]').length;

    const activeCountElement = document.getElementById('activeCount');
    const inactiveCountElement = document.getElementById('inactiveCount');

    if (activeCountElement) activeCountElement.textContent = activeDevices;
    if (inactiveCountElement) inactiveCountElement.textContent = inactiveDevices;
}

function initializeSearch() {
    const searchInput = document.getElementById('deviceSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const deviceCards = document.querySelectorAll('.device-card');
            
            deviceCards.forEach(card => {
                const deviceName = card.querySelector('h4').textContent.toLowerCase();
                const location = card.querySelector('p').textContent.toLowerCase();
                
                card.style.display = (deviceName.includes(searchTerm) || 
                                    location.includes(searchTerm)) ? 'block' : 'none';
            });
        });
    }
}

function initializeDeviceForm() {
    const addDeviceBtn = document.getElementById('addDeviceBtn');
    const addDeviceForm = document.getElementById('addDeviceForm');
    const closeFormBtn = document.getElementById('closeFormBtn');
    const form = document.getElementById('deviceForm');

    if (addDeviceBtn && addDeviceForm) {
        addDeviceBtn.addEventListener('click', function() {
            // Show the form with animation
            addDeviceForm.classList.remove('hidden');
            // Use setTimeout to allow the transition to work
            setTimeout(() => {
                addDeviceForm.classList.remove('opacity-0');
                addDeviceForm.classList.add('opacity-100');
                addDeviceForm.scrollIntoView({ behavior: 'smooth' });
                document.getElementById('id_name').focus();
            }, 50);
        });
    }

    if (closeFormBtn && addDeviceForm) {
        closeFormBtn.addEventListener('click', function() {
            // Hide the form with animation
            addDeviceForm.classList.add('opacity-0');
            addDeviceForm.classList.remove('opacity-100');
            // Wait for animation to complete before hiding
            setTimeout(() => {
                addDeviceForm.classList.add('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 300);
        });
    }

    if (form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Adding Device...';
                submitButton.disabled = true;
            }
        });
    }
}

function initializeAnimations() {
    const deviceCards = document.querySelectorAll('.device-card');
    deviceCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fade-in');
    });
}