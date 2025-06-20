// js/searchDevices.js
export function initSearch() {
    const deviceSearch = document.getElementById('deviceSearch');
    if (!deviceSearch) return;
    
    deviceSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const deviceCards = document.querySelectorAll('.device-card');
        
        deviceCards.forEach(card => {
            const deviceName = card.querySelector('h4').textContent.toLowerCase();
            const deviceLocation = card.querySelector('p.text-gray-600').textContent.toLowerCase();
            
            if (deviceName.includes(searchTerm) || deviceLocation.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
        
        // For table view
        const tableRows = document.querySelectorAll('#tableView tbody tr');
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