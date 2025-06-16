export function initModal() {
    const modal = document.getElementById('addDeviceModal');
    const backdrop = document.getElementById('modalBackdrop');
    const addDeviceBtn = document.getElementById('addDeviceBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    if (!modal || !addDeviceBtn) return;

    const openModal = () => {
        console.log('Opening modal'); // Debug log
        modal.classList.add('modal-open');
        backdrop.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
        modal.classList.remove('modal-open');
        backdrop.classList.remove('modal-open');
        document.body.style.overflow = '';
    };

    addDeviceBtn.addEventListener('click', openModal);
    closeModalBtn?.addEventListener('click', closeModal);
    cancelBtn?.addEventListener('click', closeModal);
    backdrop?.addEventListener('click', closeModal);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('modal-open')) {
            closeModal();
        }
    });
}