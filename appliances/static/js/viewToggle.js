// js/viewToggle.js
export function initViewToggle() {
    const viewBtns = document.querySelectorAll('.view-btn');
    const gridView = document.getElementById('gridView');
    const tableView = document.getElementById('tableView');
    
    if (viewBtns.length === 0) return;
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            viewBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
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