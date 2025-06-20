// js/main.js
import { initModal } from './initModal.js';
import { initViewToggle } from './viewToggle.js';
import { initStatusToggles } from './statusToggle.js';
import { initSearch } from './searchDevices.js';
import { initDeviceForm } from './deviceForm.js';
import { showNotification } from './helpers/showErrorNotification.js';

document.addEventListener('DOMContentLoaded', function() {
    initModal();
    initViewToggle();
    initStatusToggles();
    initSearch();
    initDeviceForm();
    
    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.getElementById('addDeviceModal').classList.contains('modal-open')) {
            closeModal();
        }
    });
});