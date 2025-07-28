// admin_dashboard.js - JavaScript for the admin dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables for dashboard elements
    const occupancyChartCanvas = document.getElementById('occupancyChart');
    const revenueChartCanvas = document.getElementById('revenueChart');
    const bookingChartCanvas = document.getElementById('bookingChart');
    
    // Dashboard Charts - Occupancy Trend
    if (occupancyChartCanvas) {
        // Data will be populated by the template, but we'll set up the chart here
        // This is a demo implementation - the real data comes from the Jinja template
        if (!window.occupancyTrendChart) {
            const ctx = occupancyChartCanvas.getContext('2d');
            window.occupancyTrendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Today'],
                    datasets: [{
                        label: 'Occupancy Rate (%)',
                        data: [65, 70, 68, 75, 80, 82, 78],
                        backgroundColor: 'rgba(13, 110, 253, 0.2)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Occupancy Rate (%)'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.raw + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Dashboard Revenue Chart - if it exists
    if (revenueChartCanvas) {
        if (!window.revenueChart) {
            const ctx = revenueChartCanvas.getContext('2d');
            window.revenueChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'Revenue ($)',
                        data: [12000, 15000, 18000, 16000, 22000, 25000, 28000, 30000, 26000, 24000, 20000, 22000],
                        backgroundColor: 'rgba(25, 135, 84, 0.5)',
                        borderColor: 'rgba(25, 135, 84, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Revenue ($)'
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Dashboard Booking Chart - if it exists
    if (bookingChartCanvas) {
        if (!window.bookingChart) {
            const ctx = bookingChartCanvas.getContext('2d');
            window.bookingChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Confirmed', 'Pending', 'Checked-in', 'Checked-out', 'Cancelled'],
                    datasets: [{
                        label: 'Bookings',
                        data: [42, 12, 25, 30, 8],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.8)',  // Success - Confirmed
                            'rgba(255, 193, 7, 0.8)',  // Warning - Pending
                            'rgba(23, 162, 184, 0.8)', // Info - Checked-in
                            'rgba(108, 117, 125, 0.8)', // Secondary - Checked-out
                            'rgba(220, 53, 69, 0.8)'   // Danger - Cancelled
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
    
    // Room management - Handling status updates
    const roomStatusSelects = document.querySelectorAll('.room-status-select');
    roomStatusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const roomId = this.dataset.roomId;
            const status = this.value;
            const roomCard = document.querySelector(`.room-card[data-room-id="${roomId}"]`);
            
            if (roomCard) {
                // Update room card appearance based on new status
                roomCard.querySelector('.room-status').textContent = status.charAt(0).toUpperCase() + status.slice(1);
                
                // Update header background color based on status
                const cardHeader = roomCard.querySelector('.card-header');
                if (cardHeader) {
                    cardHeader.className = 'card-header d-flex justify-content-between align-items-center';
                    
                    if (status === 'available') {
                        cardHeader.classList.add('bg-success', 'text-white');
                    } else if (status === 'occupied') {
                        cardHeader.classList.add('bg-danger', 'text-white');
                    } else if (status === 'maintenance') {
                        cardHeader.classList.add('bg-warning', 'text-dark');
                    } else if (status === 'cleaning') {
                        cardHeader.classList.add('bg-info', 'text-white');
                    } else {
                        cardHeader.classList.add('bg-secondary', 'text-white');
                    }
                }
            }
        });
    });
    
    // Handle check-in and check-out buttons
    const checkinButtons = document.querySelectorAll('.checkin-btn');
    const checkoutButtons = document.querySelectorAll('.checkout-btn');
    
    checkinButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const reservationId = this.dataset.reservationId;
            
            // Create a form to submit
            const form = document.createElement('form');
            form.method = 'post';
            form.action = `/admin/checkin/${reservationId}`;
            document.body.appendChild(form);
            form.submit();
        });
    });
    
    checkoutButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const reservationId = this.dataset.reservationId;
            
            // Create a form to submit
            const form = document.createElement('form');
            form.method = 'post';
            form.action = `/admin/checkout/${reservationId}`;
            document.body.appendChild(form);
            form.submit();
        });
    });
    
    // Reports page - handling tab navigation
    const reportTabs = document.querySelectorAll('.report-tab');
    const reportContents = document.querySelectorAll('.report-content');
    
    reportTabs.forEach(function(tab) {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const reportType = this.dataset.reportType;
            
            // Activate clicked tab
            reportTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show selected report content
            reportContents.forEach(function(content) {
                if (content.dataset.reportType === reportType) {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            });
        });
    });
    
    // Date range selector for reports
    const reportDateRange = document.getElementById('reportDateRange');
    if (reportDateRange) {
        flatpickr(reportDateRange, {
            mode: "range",
            dateFormat: "Y-m-d",
            maxDate: "today",
            onChange: function(selectedDates, dateStr, instance) {
                if (selectedDates.length === 2) {
                    // Redirect to the same report with new date range
                    const currentUrl = new URL(window.location.href);
                    const params = new URLSearchParams(currentUrl.search);
                    
                    params.set('start_date', formatDate(selectedDates[0]));
                    params.set('end_date', formatDate(selectedDates[1]));
                    
                    currentUrl.search = params.toString();
                    window.location.href = currentUrl.toString();
                }
            }
        });
    }
    
    // Helper function to format date as YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // Handle export buttons (CSV, PDF)
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const format = this.dataset.format;
            const reportType = this.dataset.reportType;
            
            // For CSV export, we could implement a proper export
            // For this demo, we'll just show an alert
            alert(`Exporting ${reportType} report as ${format}...`);
            
            // In a real implementation, we would:
            // 1. Make an AJAX request to an endpoint that generates the export
            // 2. Trigger a download of the generated file
        });
    });
    
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
