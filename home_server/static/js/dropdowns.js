// Dropdowns and Mobile Menu
document.addEventListener('DOMContentLoaded', function() {
    // User Dropdown
    const userMenuButton = document.getElementById('userMenuButton');
    const userDropdownMenu = document.getElementById('userDropdownMenu');

    userMenuButton?.addEventListener('click', function(e) {
        e.stopPropagation();
        userDropdownMenu?.classList.toggle('active');
    });

    // Mobile Menu
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');

    mobileMenuToggle?.addEventListener('click', function() {
        mobileMenu?.classList.toggle('hidden');
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!userMenuButton?.contains(e.target)) {
            userDropdownMenu?.classList.remove('active');
        }
        if (!mobileMenuToggle?.contains(e.target)) {
            mobileMenu?.classList.add('hidden');
        }
    });
});