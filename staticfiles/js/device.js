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

    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }

    statusToggles.forEach(toggle => {
        toggle.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const deviceId = this.dataset.deviceId;
            if (!deviceId) {
                console.error('Device ID not found');
                return;
            }

            const isCurrentlyOn = this.dataset.status === 'on';
            const newStatus = isCurrentlyOn ? 'off' : 'on';
            
            // Cache UI elements
            const bg = this.querySelector('.status-toggle-bg');
            const handle = this.querySelector('.status-toggle-handle');
            
            // Find status badge - search in both grid and table views
            const deviceCard = this.closest('.device-card');
            const tableRow = this.closest('tr');
            const statusBadge = deviceCard ? 
                deviceCard.querySelector('.status-badge') : 
                tableRow ? tableRow.querySelector('.status-badge') : null;
            
            // Show loading state
            if (handle) {
                handle.innerHTML = '<i class="fas fa-spinner fa-spin text-xs"></i>';
            }
            
            try {
                const response = await fetch(`/control/toggle/${deviceId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'Accept': 'application/json'
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ 
                        status: newStatus === 'on',
                        device_id: deviceId 
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    // Update toggle state
                    this.dataset.status = newStatus;
                    
                    // Update toggle appearance
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
                        handle.innerHTML = ''; // Clear loading spinner
                    }

                    // Update status badge if it exists
                    if (statusBadge) {
                        updateStatusBadge(statusBadge, newStatus);
                    }

                    // Update device counts
                    updateDeviceCounts();
                } else {
                    throw new Error(data.error || 'Failed to update device status');
                }
            } catch (error) {
                console.error('Error toggling device status:', error);
                // Revert toggle state
                this.dataset.status = isCurrentlyOn ? 'on' : 'off';
                if (handle) handle.innerHTML = '';
                
                // Show error notification
                showErrorNotification(error.message);
            }
        });
    });

    // Initialize device counts
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

// Helper function to update status badge
function updateStatusBadge(badge, status) {
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

// Helper function to show error notifications
function showErrorNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}