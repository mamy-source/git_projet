document.addEventListener('DOMContentLoaded', function() {
    // Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });
    
    // Initialize Charts
    const bookingsCtx = document.getElementById('bookingsChart').getContext('2d');
    const servicesCtx = document.getElementById('servicesChart').getContext('2d');
    
    // Bookings Chart
    const bookingsChart = new Chart(bookingsCtx, {
        type: 'line',
        data: {
            labels: ['1 Mai', '5 Mai', '10 Mai', '15 Mai', '20 Mai', '25 Mai', '30 Mai'],
            datasets: [{
                label: 'Réservations',
                data: [45, 60, 75, 82, 78, 90, 110],
                backgroundColor: 'rgba(161, 140, 209, 0.2)',
                borderColor: 'rgba(161, 140, 209, 1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    // Services Chart
    const servicesChart = new Chart(servicesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Manucure', 'Massage', 'Coiffure', 'Épilation', 'Maquillage'],
            datasets: [{
                data: [35, 25, 20, 12, 8],
                backgroundColor: [
                    'rgba(255, 154, 158, 0.8)',
                    'rgba(161, 140, 209, 0.8)',
                    'rgba(255, 195, 113, 0.8)',
                    'rgba(79, 172, 254, 0.8)',
                    'rgba(251, 194, 235, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            },
            cutout: '70%'
        }
    });
    
    // Notification Badge Click
    const notificationBadge = document.querySelector('.notifications');
    
    notificationBadge.addEventListener('click', function() {
        alert('Vous avez 3 nouvelles notifications');
    });
    
    // Action Buttons in Table
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            // In a real app, this would open a dropdown menu
            alert('Menu d\'actions');
        });
    });
    
    // Simulate loading data
    setTimeout(() => {
        document.querySelectorAll('.card').forEach(card => {
            card.style.transform = 'translateY(0)';
        });
    }, 100);
});