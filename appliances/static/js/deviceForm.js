
// deviceForm.js
export default function initializeDeviceForm() {
    const addBtn = document.getElementById('addDeviceBtn');
    const formWrapper = document.getElementById('addDeviceForm');
    const closeBtn = document.getElementById('closeFormBtn');
    const form = document.getElementById('deviceForm');

    if (addBtn && formWrapper) {
        addBtn.addEventListener('click', () => {
            formWrapper.classList.remove('hidden');
            setTimeout(() => {
                formWrapper.classList.remove('opacity-0');
                formWrapper.classList.add('opacity-100');
                formWrapper.scrollIntoView({ behavior: 'smooth' });
                document.getElementById('id_name').focus();
            }, 50);
        });
    }

    if (closeBtn && formWrapper) {
        closeBtn.addEventListener('click', () => {
            formWrapper.classList.add('opacity-0');
            formWrapper.classList.remove('opacity-100');
            setTimeout(() => {
                formWrapper.classList.add('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 300);
        });
    }

    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Adding Device...';
                submitBtn.disabled = true;
            }
        });
    }
}