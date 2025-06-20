// js/initModal.js
export function initModal() {
    const addDeviceBtn = document.getElementById('addDeviceBtn');
    const emptyStateBtn = document.getElementById('emptyStateBtn');
    const modal = document.getElementById('addDeviceModal');
    const backdrop = document.getElementById('modalBackdrop');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    
    // Open modal function
    function openModal() {
        modal.classList.add('modal-open');
        backdrop.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        setTimeout(() => {
            const firstInput = modal.querySelector('input[type="text"]');
            if (firstInput) firstInput.focus();
        }, 300);
    }
    
    // Close modal function
    function closeModal() {
        modal.classList.remove('modal-open');
        backdrop.classList.remove('modal-open');
        document.body.style.overflow = '';
    }
    
    // Event listeners for opening modal
    if (addDeviceBtn) {
        addDeviceBtn.addEventListener('click', openModal);
    }
    
    if (emptyStateBtn) {
        emptyStateBtn.addEventListener('click', openModal);
    }
    
    // Event listeners for closing modal
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }
    
    if (backdrop) {
        backdrop.addEventListener('click', closeModal);
    }
    
    return { openModal, closeModal };
}