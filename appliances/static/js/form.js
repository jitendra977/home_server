export function initializeFormElements() {
    // Initialize room dropdown
    const roomSelect = document.getElementById('id_room');
    if (roomSelect) {
        roomSelect.classList.add(
            'w-full',
            'rounded-lg',
            'bg-white/10',
            'dark:bg-black/10',
            'border',
            'border-gray-300/50',
            'dark:border-gray-700/50',
            'text-gray-900',
            'dark:text-gray-100',
            'py-2',
            'px-3',
            'focus:ring-2',
            'focus:ring-blue-500',
            'focus:border-transparent'
        );
    }

    // Initialize user dropdown
    const userSelect = document.getElementById('id_user');
    if (userSelect) {
        userSelect.classList.add(
            'w-full',
            'rounded-lg',
            'bg-white/10',
            'dark:bg-black/10',
            'border',
            'border-gray-300/50',
            'dark:border-gray-700/50',
            'text-gray-900',
            'dark:text-gray-100',
            'py-2',
            'px-3',
            'focus:ring-2',
            'focus:ring-blue-500',
            'focus:border-transparent'
        );
    }

    // Initialize name input
    const nameInput = document.getElementById('id_name');
    if (nameInput) {
        nameInput.classList.add(
            'w-full',
            'rounded-lg',
            'bg-white/10',
            'dark:bg-black/10',
            'border',
            'border-gray-300/50',
            'dark:border-gray-700/50',
            'text-gray-900',
            'dark:text-gray-100',
            'py-2',
            'px-3',
            'focus:ring-2',
            'focus:ring-blue-500',
            'focus:border-transparent'
        );
    }
}