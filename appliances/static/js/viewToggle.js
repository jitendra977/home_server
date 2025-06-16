// viewToggle.js
export default function initializeViewToggle() {
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
