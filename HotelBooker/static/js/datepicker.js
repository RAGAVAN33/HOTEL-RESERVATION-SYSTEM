// datepicker.js - JavaScript for date picker functionality in Hotel Reservation System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flatpickr date pickers
    const checkInPickers = document.querySelectorAll('input[name="check_in"]');
    const checkOutPickers = document.querySelectorAll('input[name="check_out"]');
    
    // Get today's date and tomorrow's date
    const today = new Date();
    const tomorrow = new Date();
    tomorrow.setDate(today.getDate() + 1);
    
    // Format dates as YYYY-MM-DD
    const formatDate = function(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };
    
    // Initialize all check-in date pickers
    if (checkInPickers.length > 0) {
        checkInPickers.forEach(function(picker) {
            const checkInFp = flatpickr(picker, {
                dateFormat: "Y-m-d",
                minDate: "today",
                defaultDate: picker.value || "today",
                onChange: function(selectedDates, dateStr, instance) {
                    // Find the corresponding check-out picker
                    const form = picker.closest('form');
                    if (form) {
                        const checkOutPicker = form.querySelector('input[name="check_out"]');
                        if (checkOutPicker && checkOutPicker._flatpickr) {
                            // Update the min date for check-out to be after check-in
                            const minCheckOutDate = new Date(selectedDates[0]);
                            minCheckOutDate.setDate(minCheckOutDate.getDate() + 1);
                            
                            checkOutPicker._flatpickr.set('minDate', minCheckOutDate);
                            
                            // If check-out date is before check-in date, update it
                            const checkOutDate = checkOutPicker._flatpickr.selectedDates[0];
                            if (checkOutDate <= selectedDates[0]) {
                                checkOutPicker._flatpickr.setDate(minCheckOutDate);
                            }
                        }
                    }
                    
                    // Update any related elements (e.g., night calculations)
                    updateNightCount(form);
                }
            });
        });
    }
    
    // Initialize all check-out date pickers
    if (checkOutPickers.length > 0) {
        checkOutPickers.forEach(function(picker) {
            // Calculate min date (day after check-in or tomorrow)
            let minDate = tomorrow;
            const form = picker.closest('form');
            if (form) {
                const checkInPicker = form.querySelector('input[name="check_in"]');
                if (checkInPicker && checkInPicker.value) {
                    const checkInDate = new Date(checkInPicker.value);
                    const nextDay = new Date(checkInDate);
                    nextDay.setDate(checkInDate.getDate() + 1);
                    if (nextDay > tomorrow) {
                        minDate = nextDay;
                    }
                }
            }
            
            const checkOutFp = flatpickr(picker, {
                dateFormat: "Y-m-d",
                minDate: minDate,
                defaultDate: picker.value || formatDate(tomorrow),
                onChange: function(selectedDates, dateStr, instance) {
                    // Update any related elements (e.g., night calculations)
                    updateNightCount(form);
                }
            });
        });
    }
    
    // Function to update night count and price calculations
    function updateNightCount(form) {
        if (!form) return;
        
        const checkInInput = form.querySelector('input[name="check_in"]');
        const checkOutInput = form.querySelector('input[name="check_out"]');
        const nightsElement = form.querySelector('.nights-count') || document.querySelector('.nights-count');
        const totalPriceElement = form.querySelector('.total-price') || document.querySelector('.total-price');
        
        if (checkInInput && checkOutInput && checkInInput.value && checkOutInput.value) {
            const checkInDate = new Date(checkInInput.value);
            const checkOutDate = new Date(checkOutInput.value);
            
            // Calculate nights
            const timeDiff = checkOutDate.getTime() - checkInDate.getTime();
            const nights = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            // Update nights display if element exists
            if (nightsElement) {
                nightsElement.textContent = nights;
            }
            
            // Update total price if element exists
            if (totalPriceElement && totalPriceElement.dataset.pricePerNight) {
                const pricePerNight = parseFloat(totalPriceElement.dataset.pricePerNight);
                const totalPrice = (pricePerNight * nights).toFixed(2);
                totalPriceElement.textContent = '$' + totalPrice;
            }
            
            // If there's a price breakdown section, update it
            const subtotalElement = form.querySelector('.subtotal-price') || document.querySelector('.subtotal-price');
            const taxesElement = form.querySelector('.taxes-price') || document.querySelector('.taxes-price');
            
            if (subtotalElement && taxesElement && subtotalElement.dataset.pricePerNight) {
                const pricePerNight = parseFloat(subtotalElement.dataset.pricePerNight);
                const subtotal = pricePerNight * nights;
                const taxes = subtotal * 0.1; // Assuming 10% tax rate
                const total = subtotal + taxes;
                
                subtotalElement.textContent = '$' + subtotal.toFixed(2);
                taxesElement.textContent = '$' + taxes.toFixed(2);
                
                if (totalPriceElement) {
                    totalPriceElement.textContent = '$' + total.toFixed(2);
                }
            }
        }
    }
    
    // Initialize any standalone date pickers (not check-in/check-out related)
    const datePickers = document.querySelectorAll('.datepicker:not([name="check_in"]):not([name="check_out"])');
    if (datePickers.length > 0) {
        datePickers.forEach(function(picker) {
            flatpickr(picker, {
                dateFormat: "Y-m-d",
                defaultDate: picker.value || "today"
            });
        });
    }
    
    // Check if date range pickers need to be initialized
    const dateRangePickers = document.querySelectorAll('.daterangepicker');
    if (dateRangePickers.length > 0) {
        dateRangePickers.forEach(function(picker) {
            const rangePicker = flatpickr(picker, {
                mode: "range",
                dateFormat: "Y-m-d",
                defaultDate: picker.value ? picker.value.split(' to ') : [today, tomorrow]
            });
        });
    }
});
