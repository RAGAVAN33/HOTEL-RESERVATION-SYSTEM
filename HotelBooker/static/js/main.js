// main.js - Primary JavaScript file for Hotel Reservation System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Setup for auto-dismissing alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Handle back button in browsers
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            window.location.reload();
        }
    });

    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Add current date to the footer if applicable
    const footerYear = document.getElementById('currentYear');
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }

    // Handle currency formatting
    const currencyElements = document.querySelectorAll('.format-currency');
    currencyElements.forEach(function(element) {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = '$' + value.toFixed(2);
        }
    });

    // Handle date formatting
    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(function(element) {
        const dateString = element.textContent;
        try {
            const date = new Date(dateString);
            if (!isNaN(date.getTime())) {
                element.textContent = date.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                });
            }
        } catch (e) {
            console.error('Error formatting date:', e);
        }
    });

    // Handle mobile navigation
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('mobile-nav-open');
        });
    }

    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(function(element) {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (elementPosition < windowHeight - 50) {
                element.classList.add('animated');
            }
        });
    };

    // Call once to check for visible elements on page load
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);

    // Handle print button functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Global utility functions

/**
 * Format a number as currency
 * @param {number} amount - The amount to format
 * @param {string} currencySymbol - The currency symbol to use (default: $)
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currencySymbol = '$') {
    return currencySymbol + parseFloat(amount).toFixed(2);
}

/**
 * Format a date string to a readable format
 * @param {string} dateString - The date string to format
 * @param {string} format - The format to use (default: 'short')
 * @returns {string} Formatted date string
 */
function formatDate(dateString, format = 'short') {
    const date = new Date(dateString);
    if (isNaN(date)) return dateString;
    
    switch (format) {
        case 'short':
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        case 'long':
            return date.toLocaleDateString('en-US', { 
                weekday: 'long',
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        case 'time':
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        case 'full':
            return date.toLocaleDateString('en-US', { 
                weekday: 'long',
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            }) + ' at ' + date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        default:
            return date.toLocaleDateString();
    }
}

/**
 * Calculate the number of nights between two dates
 * @param {string} checkInDate - Check-in date string (YYYY-MM-DD)
 * @param {string} checkOutDate - Check-out date string (YYYY-MM-DD)
 * @returns {number} Number of nights
 */
function calculateNights(checkInDate, checkOutDate) {
    const start = new Date(checkInDate);
    const end = new Date(checkOutDate);
    const timeDiff = end.getTime() - start.getTime();
    const nights = Math.ceil(timeDiff / (1000 * 3600 * 24));
    return nights > 0 ? nights : 0;
}

/**
 * Calculate the total price based on nightly rate and number of nights
 * @param {number} ratePerNight - Rate per night
 * @param {number} nights - Number of nights
 * @param {number} taxRate - Tax rate as decimal (default: 0.1 or 10%)
 * @returns {number} Total price including taxes
 */
function calculateTotalPrice(ratePerNight, nights, taxRate = 0.1) {
    const subtotal = ratePerNight * nights;
    const taxes = subtotal * taxRate;
    return subtotal + taxes;
}
