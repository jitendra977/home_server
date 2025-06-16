export function initializeSearch() {
    const deviceSearch = document.getElementById('deviceSearch');
    if (!deviceSearch) return;

    deviceSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const deviceCards = document.querySelectorAll('.device-card');
        const tableRows = document.querySelectorAll('#tableView tbody tr');

        deviceCards.forEach(card => {
            const deviceName = card.querySelector('h4').textContent.toLowerCase();
            const deviceLocation = card.querySelector('p.text-gray-600').textContent.toLowerCase();
            card.style.display = (deviceName.includes(searchTerm) || deviceLocation.includes(searchTerm)) 
                ? 'block' 
                : 'none';
        });

        tableRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let shouldShow = false;
            
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchTerm)) {
                    shouldShow = true;
                }
            });
            
            row.style.display = shouldShow ? 'table-row' : 'none';
        });
    });
}