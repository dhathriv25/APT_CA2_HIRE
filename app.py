from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import random
import math
import requests

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hire-platform-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after initializing db
from models import Customer, Provider, ServiceCategory, ProviderCategory, Address, Booking, Payment

# Import services
from services import find_matching_providers, calculate_distance, verify_otp

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Add initial service categories if none exist
    if ServiceCategory.query.count() == 0:
        categories = [
            ServiceCategory(name="Plumbing", description="All plumbing services"),
            ServiceCategory(name="Electrical", description="Electrical repairs and installations"),
            ServiceCategory(name="Cleaning", description="Home cleaning services"),
            ServiceCategory(name="Carpentry", description="Woodwork and furniture repairs"),
            ServiceCategory(name="Painting", description="Interior and exterior painting")
        ]
        db.session.add_all(categories)
        db.session.commit()

# Helper functions
def get_current_user():
    """Get the current logged-in user"""
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    if not user_id or not user_type:
        return None
    
    if user_type == 'customer':
        return Customer.query.get(user_id)
    elif user_type == 'provider':
        return Provider.query.get(user_id)
    
    return None

# Routes
@app.route('/')
def index():
    """Home page"""
    categories = ServiceCategory.query.all()
    top_providers = Provider.query.filter(Provider.avg_rating.isnot(None)).order_by(Provider.avg_rating.desc()).limit(5).all()
    return render_template('index.html', categories=categories, top_providers=top_providers, user=get_current_user())

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Customer registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        
        # Simple validation
        if not all([email, phone, first_name, last_name, password]):
            flash('All fields are required', 'danger')
            return render_template('customer/register.html')
        
        # Check if email already exists
        if Customer.query.filter_by(email=email).first() or Provider.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('customer/register.html')
        
        # Create new customer
        customer = Customer(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(customer)
        db.session.commit()
        
        # Generate and "send" OTP (we'll just display it for demo purposes)
        otp_code = ''.join(random.choices('0123456789', k=6))
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        session['otp_code'] = otp_code
        session['otp_expiry'] = otp_expiry.strftime('%Y-%m-%d %H:%M:%S')
        session['temp_user_id'] = customer.id
        session['temp_user_type'] = 'customer'
        
        flash(f'Account created! Your verification code is: {otp_code}', 'success')
        return redirect(url_for('verify_otp'))
    
    return render_template('customer/register.html')

@app.route('/provider/register', methods=['GET', 'POST'])
def provider_register():
    """Provider registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        experience_years = int(request.form.get('experience_years', 0))
        
        # Simple validation
        if not all([email, phone, first_name, last_name, password]):
            flash('All fields are required', 'danger')
            return render_template('provider/register.html')
        
        # Check if email already exists
        if Customer.query.filter_by(email=email).first() or Provider.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('provider/register.html')
        
        # Create new provider
        provider = Provider(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password_hash=generate_password_hash(password),
            experience_years=experience_years,
            verification_document='verification_placeholder.pdf'  # Placeholder
        )
        db.session.add(provider)
        db.session.commit()
        
        # Generate and "send" OTP (we'll just display it for demo purposes)
        otp_code = ''.join(random.choices('0123456789', k=6))
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        session['otp_code'] = otp_code
        session['otp_expiry'] = otp_expiry.strftime('%Y-%m-%d %H:%M:%S')
        session['temp_user_id'] = provider.id
        session['temp_user_type'] = 'provider'
        
        flash(f'Account created! Your verification code is: {otp_code}', 'success')
        return redirect(url_for('verify_otp'))
    
    return render_template('provider/register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP verification"""
    if 'temp_user_id' not in session or 'temp_user_type' not in session:
        flash('Please register first', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['temp_user_id']
    user_type = session['temp_user_type']
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp_code')
        
        if not entered_otp:
            flash('Please enter the verification code', 'danger')
            return render_template('verify_otp.html')
        
        # Verify OTP (this is a simplified implementation)
        if verify_otp(entered_otp, session.get('otp_code'), session.get('otp_expiry')):
            # Mark user as verified
            if user_type == 'customer':
                user = Customer.query.get(user_id)
                if user:
                    user.is_verified = True
                    db.session.commit()
                    
                    # Log user in
                    session.pop('temp_user_id', None)
                    session.pop('temp_user_type', None)
                    session.pop('otp_code', None)
                    session.pop('otp_expiry', None)
                    session['user_id'] = user.id
                    session['user_type'] = 'customer'
                    
                    flash('Email verified successfully! You are now logged in.', 'success')
                    return redirect(url_for('customer_dashboard'))
            
            elif user_type == 'provider':
                user = Provider.query.get(user_id)
                if user:
                    user.is_verified = True
                    db.session.commit()
                    
                    # Log user in
                    session.pop('temp_user_id', None)
                    session.pop('temp_user_type', None)
                    session.pop('otp_code', None)
                    session.pop('otp_expiry', None)
                    session['user_id'] = user.id
                    session['user_type'] = 'provider'
                    
                    flash('Email verified successfully! You are now logged in.', 'success')
                    return redirect(url_for('provider_dashboard'))
        
        flash('Invalid or expired verification code', 'danger')
    
    return render_template('verify_otp.html')

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('customer/login.html')
        
        customer = Customer.query.filter_by(email=email).first()
        
        if not customer or not check_password_hash(customer.password_hash, password):
            flash('Invalid email or password', 'danger')
            return render_template('customer/login.html')
        
        if not customer.is_verified:
            flash('Please verify your email first', 'warning')
            return render_template('customer/login.html')
        
        # Log user in
        session['user_id'] = customer.id
        session['user_type'] = 'customer'
        
        flash('You are now logged in', 'success')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('customer/login.html')

@app.route('/provider/login', methods=['GET', 'POST'])
def provider_login():
    """Provider login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('provider/login.html')
        
        provider = Provider.query.filter_by(email=email).first()
        
        if not provider or not check_password_hash(provider.password_hash, password):
            flash('Invalid email or password', 'danger')
            return render_template('provider/login.html')
        
        if not provider.is_verified:
            flash('Please verify your email first', 'warning')
            return render_template('provider/login.html')
        
        # Log user in
        session['user_id'] = provider.id
        session['user_type'] = 'provider'
        
        flash('You are now logged in', 'success')
        return redirect(url_for('provider_dashboard'))
    
    return render_template('provider/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/customer/dashboard')
def customer_dashboard():
    """Customer dashboard"""
    customer = get_current_user()
    
    if not customer or not isinstance(customer, Customer):
        flash('Please log in as a customer', 'warning')
        return redirect(url_for('customer_login'))
    
    # Get customer's bookings
    bookings = Booking.query.filter_by(customer_id=customer.id).order_by(Booking.created_at.desc()).all()
    
    return render_template('customer/dashboard.html', customer=customer, bookings=bookings)

@app.route('/provider/dashboard')
def provider_dashboard():
    """Provider dashboard"""
    provider = get_current_user()
    
    if not provider or not isinstance(provider, Provider):
        flash('Please log in as a provider', 'warning')
        return redirect(url_for('provider_login'))
    
    # Get provider's bookings
    bookings = Booking.query.filter_by(provider_id=provider.id).order_by(Booking.created_at.desc()).all()
    
    # Get provider's services
    services = ProviderCategory.query.filter_by(provider_id=provider.id).all()
    
    return render_template('provider/dashboard.html', provider=provider, bookings=bookings, services=services)

@app.route('/services')
def service_list():
    """List all service categories"""
    categories = ServiceCategory.query.all()
    return render_template('services/list.html', categories=categories, user=get_current_user())

@app.route('/services/<int:category_id>')
def service_detail(category_id):
    """Show details of a specific service category"""
    category = ServiceCategory.query.get_or_404(category_id)
    
    # Get providers for this category
    provider_categories = ProviderCategory.query.filter_by(category_id=category_id).all()
    providers = [pc.provider for pc in provider_categories if pc.provider.is_verified]
    
    return render_template('services/detail.html', category=category, providers=providers, user=get_current_user())

@app.route('/provider/services/add', methods=['GET', 'POST'])
def add_provider_service():
    """Add a service category for a provider"""
    provider = get_current_user()
    
    if not provider or not isinstance(provider, Provider):
        flash('Please log in as a provider', 'warning')
        return redirect(url_for('provider_login'))
    
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        price_rate = request.form.get('price_rate')
        
        if not category_id or not price_rate:
            flash('All fields are required', 'danger')
            return redirect(url_for('add_provider_service'))
        
        # Check if provider already offers this service
        existing = ProviderCategory.query.filter_by(provider_id=provider.id, category_id=category_id).first()
        if existing:
            flash('You already offer this service', 'warning')
            return redirect(url_for('provider_dashboard'))
        
        # Add new provider-category association
        provider_category = ProviderCategory(
            provider_id=provider.id,
            category_id=category_id,
            price_rate=float(price_rate)
        )
        db.session.add(provider_category)
        db.session.commit()
        
        flash('Service added successfully', 'success')
        return redirect(url_for('provider_dashboard'))
    
    # Get categories not already offered by this provider
    existing_categories = ProviderCategory.query.filter_by(provider_id=provider.id).with_entities(ProviderCategory.category_id).all()
    existing_category_ids = [ec.category_id for ec in existing_categories]
    
    available_categories = ServiceCategory.query.filter(~ServiceCategory.id.in_(existing_category_ids)).all()
    
    return render_template('provider/add_service.html', categories=available_categories)

@app.route('/customer/address/add', methods=['GET', 'POST'])
def add_address():
    """Add a new address for a customer"""
    customer = get_current_user()
    
    if not customer or not isinstance(customer, Customer):
        flash('Please log in as a customer', 'warning')
        return redirect(url_for('customer_login'))
    
    if request.method == 'POST':
        address_line = request.form.get('address_line')
        city = request.form.get('city')
        state = request.form.get('state')
        postal_code = request.form.get('postal_code')
        
        if not all([address_line, city, state, postal_code]):
            flash('All fields are required', 'danger')
            return render_template('customer/add_address.html')
        
        # Create new address
        address = Address(
            customer_id=customer.id,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code
        )
        
        # Try to geocode the address
        full_address = f"{address_line}, {city}, {state} {postal_code}"
        
        try:
            # Call the geocoding API
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'HIRE Platform/1.0'
            }
            
            response = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    address.latitude = float(data[0]['lat'])
                    address.longitude = float(data[0]['lon'])
        except Exception as e:
            # Just log the error and continue (geocoding is not critical)
            print(f"Geocoding error: {e}")
        
        db.session.add(address)
        db.session.commit()
        
        flash('Address added successfully', 'success')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('customer/add_address.html')

@app.route('/booking/create/<int:provider_id>', methods=['GET', 'POST'])
def create_booking(provider_id):
    """Create a new booking"""
    customer = get_current_user()
    
    if not customer or not isinstance(customer, Customer):
        flash('Please log in as a customer', 'warning')
        return redirect(url_for('customer_login'))
    
    provider = Provider.query.get_or_404(provider_id)
    
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        address_id = request.form.get('address_id')
        booking_date = request.form.get('booking_date')
        time_slot = request.form.get('time_slot')
        
        if not all([category_id, address_id, booking_date, time_slot]):
            flash('All fields are required', 'danger')
            return redirect(url_for('create_booking', provider_id=provider_id))
        
        # Create new booking
        booking = Booking(
            customer_id=customer.id,
            provider_id=provider_id,
            category_id=category_id,
            address_id=address_id,
            booking_date=datetime.strptime(booking_date, '%Y-%m-%d').date(),
            time_slot=time_slot,
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking created successfully', 'success')
        return redirect(url_for('payment_process', booking_id=booking.id))
    
    # Get services offered by this provider
    provider_categories = ProviderCategory.query.filter_by(provider_id=provider_id).all()
    
    # Get customer's addresses
    addresses = Address.query.filter_by(customer_id=customer.id).all()
    
    # If no addresses, redirect to add address page
    if not addresses:
        flash('Please add an address first', 'warning')
        return redirect(url_for('add_address'))
    
    # Get available time slots (simplified)
    time_slots = [
        '09:00-10:00', '10:00-11:00', '11:00-12:00',
        '13:00-14:00', '14:00-15:00', '15:00-16:00',
        '16:00-17:00', '17:00-18:00'
    ]
    
    return render_template(
        'booking/create.html',
        provider=provider,
        provider_categories=provider_categories,
        addresses=addresses,
        time_slots=time_slots,
        min_date=datetime.now().date() + timedelta(days=1)
    )

@app.route('/booking/<int:booking_id>')
def booking_detail(booking_id):
    """Show booking details"""
    user = get_current_user()
    
    if not user:
        flash('Please log in', 'warning')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to view this booking
    if (isinstance(user, Customer) and booking.customer_id != user.id) or \
       (isinstance(user, Provider) and booking.provider_id != user.id):
        flash('You are not authorized to view this booking', 'danger')
        return redirect(url_for('index'))
    
    return render_template('booking/detail.html', booking=booking, user=user)

@app.route('/payment/process/<int:booking_id>', methods=['GET', 'POST'])
def payment_process(booking_id):
    """Process payment for a booking"""
    customer = get_current_user()
    
    if not customer or not isinstance(customer, Customer):
        flash('Please log in as a customer', 'warning')
        return redirect(url_for('customer_login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if customer owns this booking
    if booking.customer_id != customer.id:
        flash('You are not authorized to pay for this booking', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    # Check if booking is pending
    if booking.status != 'pending':
        flash('This booking cannot be paid for', 'warning')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    # Calculate payment amount
    provider_category = ProviderCategory.query.filter_by(
        provider_id=booking.provider_id,
        category_id=booking.category_id
    ).first()
    
    if not provider_category:
        flash('Invalid booking', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    amount = provider_category.price_rate
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Please select a payment method', 'danger')
            return redirect(url_for('payment_process', booking_id=booking_id))
        
        # Create payment (simplified)
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=f"HIRE-{random.randint(10000, 99999)}",
            status='successful'  # Always successful for demo purposes
        )
        db.session.add(payment)
        
        # Update booking status
        booking.status = 'confirmed'
        
        db.session.commit()
        
        flash('Payment processed successfully', 'success')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    return render_template('payment/process.html', booking=booking, amount=amount)

@app.route('/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    user = get_current_user()
    
    if not user:
        flash('Please log in', 'warning')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to cancel this booking
    if (isinstance(user, Customer) and booking.customer_id != user.id) or \
       (isinstance(user, Provider) and booking.provider_id != user.id):
        flash('You are not authorized to cancel this booking', 'danger')
        return redirect(url_for('index'))
    
    # Check if booking can be cancelled
    if booking.status not in ['pending', 'confirmed']:
        flash('This booking cannot be cancelled', 'warning')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    # Cancel booking
    booking.status = 'cancelled'
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    
    if isinstance(user, Customer):
        return redirect(url_for('customer_dashboard'))
    else:
        return redirect(url_for('provider_dashboard'))

@app.route('/booking/<int:booking_id>/complete', methods=['POST'])
def complete_booking(booking_id):
    """Mark a booking as completed"""
    provider = get_current_user()
    
    if not provider or not isinstance(provider, Provider):
        flash('Please log in as a provider', 'warning')
        return redirect(url_for('provider_login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if provider owns this booking
    if booking.provider_id != provider.id:
        flash('You are not authorized to complete this booking', 'danger')
        return redirect(url_for('provider_dashboard'))
    
    # Check if booking can be completed
    if booking.status != 'confirmed':
        flash('This booking cannot be marked as completed', 'warning')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    # Complete booking
    booking.status = 'completed'
    db.session.commit()
    
    flash('Booking marked as completed successfully', 'success')
    return redirect(url_for('provider_dashboard'))

@app.route('/booking/<int:booking_id>/rate', methods=['POST'])
def rate_booking(booking_id):
    """Rate a completed booking"""
    customer = get_current_user()
    
    if not customer or not isinstance(customer, Customer):
        flash('Please log in as a customer', 'warning')
        return redirect(url_for('customer_login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if customer owns this booking
    if booking.customer_id != customer.id:
        flash('You are not authorized to rate this booking', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    # Check if booking can be rated
    if booking.status != 'completed' or booking.rating is not None:
        flash('This booking cannot be rated', 'warning')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if not rating:
        flash('Please provide a rating', 'danger')
        return redirect(url_for('booking_detail', booking_id=booking_id))
    
    # Update booking with rating
    booking.rating = int(rating)
    booking.rating_comment = comment
    
    # Update provider's average rating
    provider = Provider.query.get(booking.provider_id)
    rated_bookings = Booking.query.filter_by(
        provider_id=provider.id,
        status='completed'
    ).filter(Booking.rating.isnot(None)).all()
    
    total_rating = sum(b.rating for b in rated_bookings)
    provider.avg_rating = round(total_rating / len(rated_bookings), 2)
    
    db.session.commit()
    
    flash('Booking rated successfully', 'success')
    return redirect(url_for('booking_detail', booking_id=booking_id))

@app.route('/search', methods=['GET'])
def search_providers():
    """Search for providers based on service category and location"""
    category_id = request.args.get('category_id')
    address_id = request.args.get('address_id')
    
    if not category_id:
        flash('Please select a service category', 'warning')
        return redirect(url_for('service_list'))
    
    category = ServiceCategory.query.get_or_404(category_id)
    
    # Find providers for this category
    provider_categories = ProviderCategory.query.filter_by(category_id=category_id).all()
    providers = [pc.provider for pc in provider_categories if pc.provider.is_verified]
    
    # If address is provided, sort providers by distance
    if address_id:
        address = Address.query.get(address_id)
        if address and address.latitude and address.longitude:
            # Calculate distance for each provider and sort
            provider_distances = []
            for provider in providers:
                # Get provider's address
                provider_address = Address.query.filter_by(provider_id=provider.id).first()
                
                if provider_address and provider_address.latitude and provider_address.longitude:
                    distance = calculate_distance(
                        address.latitude, address.longitude,
                        provider_address.latitude, provider_address.longitude
                    )
                else:
                    distance = float('inf')  # If provider has no address, put at end of list
                
                provider_distances.append((provider, distance))
            
            # Sort by distance
            provider_distances.sort(key=lambda x: x[1])
            providers = [p[0] for p in provider_distances]
    
    return render_template(
        'search_results.html',
        category=category,
        providers=providers,
        user=get_current_user()
    )

if __name__ == '__main__':
    app.run(debug=True)