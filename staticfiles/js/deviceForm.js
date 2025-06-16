export function initializeModal() {
    const addDeviceBtn = document.getElementById('addDeviceBtn');
    const emptyStateBtn = document.getElementById('emptyStateBtn');
    const modal = document.getElementById('addDeviceModal');
    const backdrop = document.getElementById('modalBackdrop');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const deviceForm = document.getElementById('deviceForm');

    function openModal() {
        modal.classList.add('modal-open');
        backdrop.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        
        setTimeout(() => {
            const firstInput = modal.querySelector('input[type="text"]');
            if (firstInput) firstInput.focus();
        }, 300);
    }

    function closeModal() {
        modal.classList.remove('modal-open');
        backdrop.classList.remove('modal-open');
        document.body.style.overflow = '';
        if (deviceForm) deviceForm.reset();
    }

    if (addDeviceBtn) addDeviceBtn.addEventListener('click', openModal);
    if (emptyStateBtn) emptyStateBtn.addEventListener('click', openModal);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    if (deviceForm) {
        deviceForm.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('{{ form.name.id_for_label }}');
            const locationInput = document.getElementById('{{ form.location.id_for_label }}');
            
            if (!nameInput.value.trim() || !locationInput.value.trim()) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('modal-open')) {
            closeModal();
        }
    });
}