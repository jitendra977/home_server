export function initializeViewToggle() {
    const viewBtns = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('gridView');
    const tableView = document.getElementById('tableView');

    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            if (view === 'grid') {
                gridView.classList.remove('hidden');
                tableView.classList.add('hidden');
            } else if (view === 'table') {
                gridView.classList.add('hidden');
                tableView.classList.remove('hidden');
            }
        });
    });
}