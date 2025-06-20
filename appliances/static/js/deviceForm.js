// js/deviceForm.js
import { showNotification } from './helpers/showErrorNotification.js';

export function initDeviceForm() {
    const deviceForm = document.getElementById('deviceForm');
    if (!deviceForm) return;
    
    // Get closeModal from modal module
    const { closeModal } = initModal();
    
    deviceForm.addEventListener('submit', function(e) {
        const nameInput = document.getElementById('{{ form.name.id_for_label }}');
        const locationInput = document.getElementById('{{ form.location.id_for_label }}');
        
        if (!nameInput.value.trim() || !locationInput.value.trim()) {
            e.preventDefault();
            showNotification('Please fill in all required fields', 'error');
        } else {
            // Close modal on successful submission
            closeModal();
        }
    });
}