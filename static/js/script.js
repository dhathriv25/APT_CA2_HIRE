// Custom JavaScript for HIRE Platform

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert:not(.alert-warning)');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const closeBtn = message.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            } else {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            }
        }, 5000);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Rating functionality on rating forms
    const ratingInputs = document.querySelectorAll('.rating input[type="radio"]');
    ratingInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            // Highlight stars for selected rating
            const rating = parseInt(this.value);
            const stars = this.closest('.rating').querySelectorAll('.form-check-label');
            
            stars.forEach(function(star, index) {
                if (index < rating) {
                    star.style.color = '#ffc107'; // Yellow color for selected stars
                } else {
                    star.style.color = ''; // Default color for unselected stars
                }
            });
        });
    });

    // Address validation for add address form
    const addressForm = document.getElementById('address-form');
    if (addressForm) {
        addressForm.addEventListener('submit', function(event) {
            const addressLine = document.getElementById('address_line').value;
            const city = document.getElementById('city').value;
            const state = document.getElementById('state').value;
            const postalCode = document.getElementById('postal_code').value;
            
            if (!addressLine || !city || !state || !postalCode) {
                event.preventDefault();
                alert('Please fill in all address fields');
            }
        });
    }

    // Booking form validation
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            const categoryId = document.getElementById('category_id').value;
            const addressId = document.getElementById('address_id').value;
            const bookingDate = document.getElementById('booking_date').value;
            const timeSlot = document.getElementById('time_slot').value;
            
            if (!categoryId || !addressId || !bookingDate || !timeSlot) {
                event.preventDefault();
                alert('Please fill in all booking details');
            }
        });
    }

    // Payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(event) {
            const paymentMethod = document.getElementById('payment_method').value;
            
            if (!paymentMethod) {
                event.preventDefault();
                alert('Please select a payment method');
                return;
            }
            
            // For demo purposes, we'll just validate the form without actual payment processing
            if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
                const cardNumber = document.getElementById('card_number').value;
                const expiryDate = document.getElementById('expiry_date').value;
                const cvv = document.getElementById('cvv').value;
                const cardName = document.getElementById('card_name').value;
                
                if (!cardNumber || !expiryDate || !cvv || !cardName) {
                    event.preventDefault();
                    alert('Please fill in all card details');
                }
            }
        });
    }
});