document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    // Load data based on current page
    if (path === '/') {
        loadDashboardData();
    } else if (path === '/medicines') {
        loadMedicines();
    } else if (path === '/sales') {
        loadSales();
    } else if (path === '/inventory') {
        loadInventory();
    }
});

function loadDashboardData() {
    fetch('/api/medicines')
        .then(response => response.json())
        .then(medicines => {
            document.getElementById('total-medicines').textContent = medicines.length;
            document.getElementById('low-stock').textContent = 
                medicines.filter(m => m.quantity < 10).length;
        })
        .catch(error => console.error('Error loading dashboard data:', error));
}

function loadMedicines() {
    fetch('/api/medicines')
        .then(response => response.json())
        .then(medicines => {
            const tableBody = document.getElementById('medicines-body');
            if (tableBody) {
                tableBody.innerHTML = '';
                medicines.forEach(medicine => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${medicine.name}</td>
                        <td>${medicine.quantity}</td>
                        <td>$${medicine.price.toFixed(2)}</td>
                        <td>
                            <button onclick="editMedicine(${medicine.id})">Edit</button>
                            <button onclick="deleteMedicine(${medicine.id})">Delete</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error loading medicines:', error));
}