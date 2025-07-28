// room_search.js - JavaScript for the room search functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get elements for filtering and sorting
    const roomTypeFilter = document.getElementById('room_type');
    const guestsFilter = document.getElementById('guests');
    const roomSorter = document.getElementById('sort_rooms');
    const roomCards = document.querySelectorAll('.room-card');
    const noRoomsMessage = document.getElementById('no-rooms-message');
    
    // Initialize variables to track state
    let selectedRoomType = '';
    let selectedGuests = 0;
    let selectedSort = 'price-asc'; // Default sorting
    
    // Function to filter and sort rooms
    function filterAndSortRooms() {
        let visibleRooms = 0;
        
        // Loop through all room cards
        roomCards.forEach(function(card) {
            const roomType = card.getAttribute('data-room-type');
            const capacity = parseInt(card.getAttribute('data-capacity'), 10);
            const pricePerNight = parseFloat(card.getAttribute('data-price'));
            
            // Filter by room type
            const typeMatch = !selectedRoomType || roomType === selectedRoomType;
            
            // Filter by capacity (number of guests)
            const capacityMatch = !selectedGuests || capacity >= selectedGuests;
            
            // Show or hide based on filters
            if (typeMatch && capacityMatch) {
                card.style.display = 'block';
                visibleRooms++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show "no rooms found" message if no rooms match the filters
        if (noRoomsMessage) {
            if (visibleRooms === 0) {
                noRoomsMessage.style.display = 'block';
            } else {
                noRoomsMessage.style.display = 'none';
            }
        }
        
        // Sort visible rooms
        sortRooms();
    }
    
    // Function to sort room cards
    function sortRooms() {
        const roomContainer = document.querySelector('.room-container') || document.getElementById('roomsContainer');
        
        if (!roomContainer) return;
        
        // Get all visible room cards
        const visibleCards = Array.from(roomCards).filter(card => card.style.display !== 'none');
        
        // Sort based on selected sorting option
        visibleCards.sort(function(a, b) {
            const priceA = parseFloat(a.getAttribute('data-price'));
            const priceB = parseFloat(b.getAttribute('data-price'));
            const ratingA = parseFloat(a.getAttribute('data-rating') || '0');
            const ratingB = parseFloat(b.getAttribute('data-rating') || '0');
            
            if (selectedSort === 'price-asc') {
                return priceA - priceB;
            } else if (selectedSort === 'price-desc') {
                return priceB - priceA;
            } else if (selectedSort === 'rating-desc') {
                return ratingB - ratingA;
            }
            
            return 0;
        });
        
        // Reorder elements in the DOM
        visibleCards.forEach(function(card) {
            roomContainer.appendChild(card);
        });
    }
    
    // Add event listeners to filter elements
    if (roomTypeFilter) {
        roomTypeFilter.addEventListener('change', function() {
            selectedRoomType = this.value;
            filterAndSortRooms();
        });
    }
    
    if (guestsFilter) {
        guestsFilter.addEventListener('change', function() {
            selectedGuests = parseInt(this.value, 10);
            filterAndSortRooms();
        });
    }
    
    if (roomSorter) {
        roomSorter.addEventListener('change', function() {
            selectedSort = this.value;
            sortRooms();
        });
    }
    
    // Function to recalculate prices when date range changes
    function updatePrices() {
        // Get check-in and check-out dates
        const checkInInput = document.querySelector('input[name="check_in"]');
        const checkOutInput = document.querySelector('input[name="check_out"]');
        
        if (!checkInInput || !checkOutInput) return;
        
        const checkInDate = new Date(checkInInput.value);
        const checkOutDate = new Date(checkOutInput.value);
        
        // Calculate nights
        const timeDiff = checkOutDate.getTime() - checkInDate.getTime();
        const nights = Math.ceil(timeDiff / (1000 * 3600 * 24));
        
        if (nights <= 0) return;
        
        // Update nights display in all room cards
        const nightsDisplays = document.querySelectorAll('.nights-display');
        nightsDisplays.forEach(function(elem) {
            elem.textContent = nights + (nights === 1 ? ' night' : ' nights');
        });
        
        // Update total price in all room cards
        roomCards.forEach(function(card) {
            const pricePerNight = parseFloat(card.getAttribute('data-price'));
            const totalPriceElem = card.querySelector('.total-price');
            
            if (totalPriceElem) {
                const totalPrice = pricePerNight * nights;
                totalPriceElem.textContent = '$' + totalPrice.toFixed(2);
            }
        });
    }
    
    // Listen for date changes to update prices
    const dateInputs = document.querySelectorAll('input[name="check_in"], input[name="check_out"]');
    dateInputs.forEach(function(input) {
        input.addEventListener('change', updatePrices);
    });
    
    // Initialize by applying filters and updating prices
    filterAndSortRooms();
    updatePrices();
    
    // Handle room detail view if present
    const roomDetailImages = document.querySelectorAll('.room-detail-thumbnail');
    const roomMainImage = document.querySelector('.room-detail-main-image');
    
    if (roomDetailImages.length > 0 && roomMainImage) {
        roomDetailImages.forEach(function(img) {
            img.addEventListener('click', function() {
                roomMainImage.src = this.src;
                
                // Remove active class from all thumbnails and add to clicked one
                roomDetailImages.forEach(thumb => thumb.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
});
