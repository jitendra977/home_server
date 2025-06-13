// Theme Toggle
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    function setTheme(isDark) {
        if (isDark) {
            html.classList.add('dark');
            themeIcon.className = 'fas fa-moon text-blue-400 text-lg';
            localStorage.setItem('theme', 'dark');
        } else {
            html.classList.remove('dark');
            themeIcon.className = 'fas fa-sun text-yellow-500 text-lg';
            localStorage.setItem('theme', 'light');
        }
    }

    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(savedTheme ? savedTheme === 'dark' : prefersDark);

    themeToggle?.addEventListener('click', () => {
        setTheme(!html.classList.contains('dark'));
    });
});