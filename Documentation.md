# HIRE Platform - Project Report

## 1. Introduction

The HIRE platform is an information system designed to connect residential service customers with qualified service providers for household maintenance services. It addresses the challenge of finding trusted professionals for home services while providing service providers with a platform to showcase their skills and find clients.

This project was developed as part of the Advanced Programming Techniques (B9CY100) module assessment, applying various programming concepts, data structures, and algorithms to create a comprehensive, functional system.

## 2. Problem Domain Analysis

### 2.1 Problem Statement

The home service sector faces several challenges:

- **For Customers**: Finding reliable, qualified professionals for home maintenance is time-consuming and often relies on word-of-mouth recommendations. There's also a lack of transparency in pricing and service provider credentials.

- **For Service Providers**: Skilled professionals struggle to find consistent work opportunities and have limited ability to market themselves effectively. They face high marketing costs and difficulty in building a client base.

### 2.2 Solution Overview

HIRE solves these problems by creating a digital marketplace with:
- Verified provider profiles with transparent ratings and reviews
- Easy booking and scheduling system
- Secure payment processing
- Location-based provider matching
- User-friendly interfaces for both customers and providers

## 3. Requirements Specification

### 3.1 Functional Requirements

1. **User Registration and Profile Management**
   - Users should be able to register as either customers or service providers
   - Service providers require verification before offering services
   - Users can manage personal profiles and information

2. **Service Management**
   - Service providers can register for multiple service categories
   - Providers can set their own rates for each service
   - Customers can browse available services and providers

3. **Booking System**
   - Customers can book services for specific dates and times
   - System should track booking status (pending, confirmed, completed, cancelled)
   - Service providers can accept, complete, or decline bookings

4. **Rating System**
   - Customers can rate and review providers after service completion
   - System calculates and displays average provider ratings

5. **Payment Processing**
   - System should handle payment records for bookings
   - Different payment methods should be supported

6. **Location Services**
   - System should store address information with geocoding
   - Provider matching should consider location proximity

### 3.2 Non-Functional Requirements

1. **Security**: User data and payments must be securely processed
2. **Performance**: The system should handle multiple concurrent users
3. **Usability**: Intuitive interfaces for both types of users
4. **Reliability**: Consistent and reliable service for all operations
5. **Scalability**: Ability to add more services and users as the platform grows

## 4. System Architecture

### 4.1 Architectural Pattern

The HIRE platform follows a **layered architecture pattern** with clear separation of concerns:

1. **Presentation Layer**: 
   - Flask routes and Jinja2 templates handling the user interface
   - Organized using blueprints for modular code structure

2. **Business Logic Layer**: 
   - Services module containing algorithms and business rules
   - Core algorithms for provider matching, distance calculation, etc.

3. **Data Access Layer**: 
   - SQLAlchemy models for database interactions
   - ORM-based database access and management

```
┌────────────────────────────────────────┐
│           Presentation Layer           │
│  (Flask Routes, Templates, Blueprints) │
└────────────────────┬───────────────────┘
                     │
                     ▼
┌────────────────────────────────────────┐
│          Business Logic Layer          │
│    (Services, Algorithms, Business     │
│               Rules)                   │
└────────────────────┬───────────────────┘
                     │
                     ▼
┌────────────────────────────────────────┐
│           Data Access Layer            │
│          (SQLAlchemy Models)           │
└────────────────────┬───────────────────┘
                     │
                     ▼
┌────────────────────────────────────────┐
│              Database                  │
│          (SQLite/SQL Server)           │
└────────────────────────────────────────┘
```

This architecture provides several benefits:
- **Maintainability**: Changes to one layer don't affect others
- **Testability**: Each layer can be tested independently
- **Scalability**: Layers can be scaled horizontally if needed
- **Separation of concerns**: Clear division of responsibilities

### 4.2 Technologies Used

- **Backend Framework**: Flask - A lightweight Python web framework
- **Database**: SQLite (can be migrated to SQL Server)
- **ORM**: SQLAlchemy - Provides an abstraction over the database
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Template Engine**: Jinja2 for server-side rendering
- **API Integration**: OpenStreetMap/Nominatim for geocoding
- **Authentication**: Werkzeug's security utilities for password hashing
- **OTP Verification**: Twilio API for phone verification

## 5. Data Structures and Algorithms

### 5.1 Data Models

The system uses the following key data structures, implemented using SQLAlchemy models:

#### 5.1.1 Core Models

1. **Customer**: Represents end users who book services
```python
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Other fields...
    
    # Relationships
    addresses = db.relationship('Address', backref='customer', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
```

2. **Provider**: Represents service professionals
```python
class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Fields...
    verification_document = db.Column(db.String(255), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, nullable=True)
    
    # Relationships
    services = db.relationship('ProviderCategory', backref='provider', lazy=True)
    bookings = db.relationship('Booking', backref='provider', lazy=True)
```

3. **Booking**: Implements a state machine for tracking service bookings
```python
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Relationships and fields...
    
    # State machine: booking status
    STATUS_CHOICES = ['pending', 'confirmed', 'completed', 'cancelled']
    status = db.Column(db.String(20), default='pending', nullable=False)
```

4. **ServiceCategory**: Represents the types of services offered on the platform
```python
class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
```

5. **ProviderCategory**: Many-to-many relationship between providers and service categories with additional pricing information
```python
class ProviderCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    price_rate = db.Column(db.Float, nullable=False)
```

6. **Address**: Stores geographical location information with latitude and longitude for distance calculations
```python
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Fields...
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
```

7. **Payment**: Records payment information for bookings
```python
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    # Other fields...
```

8. **OTPVerification**: Stores verification codes for phone verification
```python
class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'customer' or 'provider'
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
```

### 5.2 Key Algorithms

#### 5.2.1 Provider Matching Algorithm

The provider matching algorithm (`find_matching_providers()`) is a core component that finds the most suitable service providers for a customer based on multiple factors:

```python
def find_matching_providers(customer_address, service_category_id, limit=5):
    # Get all providers for this service category who are verified and available
    provider_categories = ProviderCategory.query.filter_by(category_id=service_category_id).all()
    if not provider_categories:
        return []
    
    # Get provider IDs and providers
    provider_ids = [pc.provider_id for pc in provider_categories]
    providers = Provider.query.filter(
        Provider.id.in_(provider_ids),
        Provider.is_available == True,
        Provider.is_verified == True
    ).all()
    
    # Calculate average prices for comparison
    avg_prices = {}
    for pc in provider_categories:
        if pc.category_id not in avg_prices:
            avg_prices[pc.category_id] = []
        avg_prices[pc.category_id].append(pc.price_rate)
    
    for category_id, prices in avg_prices.items():
        avg_prices[category_id] = sum(prices) / len(prices)
    
    # Calculate scores for each provider
    provider_scores = []
    for provider in providers:
        score = calculate_provider_score(
            provider, customer_address, service_category_id, avg_prices
        )
        provider_scores.append((provider, score))
    
    # Sort by score in descending order and return top matches
    provider_scores.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in provider_scores[:limit]]
```

The scoring algorithm uses weighted criteria:
- **Provider Rating (40%)**: Higher-rated providers receive more points
- **Experience Years (30%)**: More experienced providers get higher scores
- **Price Competitiveness (30%)**: Providers charging less than average get bonus points
- **Proximity Bonus**: Providers closer to the customer's location receive additional points

This multi-criteria approach ensures customers get high-quality, reasonably priced service providers who are nearby.

#### 5.2.2 Haversine Distance Calculation

For calculating the distance between two geographical points (customer and provider), we implement the Haversine formula:

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r
```

This algorithm demonstrates the practical application of:
- Trigonometric functions
- The Haversine formula for spherical distance calculation
- Coordinate system transformation

#### 5.2.3 Booking State Machine

The Booking model implements a finite state machine pattern for tracking the lifecycle of service bookings:

- **Initial State**: `pending` (booking created but not paid)
- **Valid Transitions**:
  - `pending` → `confirmed` (after payment)
  - `pending` → `cancelled` (customer cancels)
  - `confirmed` → `completed` (service performed)
  - `confirmed` → `cancelled` (customer or provider cancels)

This pattern encapsulates booking state logic and ensures only valid state transitions are allowed.

## 6. API Integration

### 6.1 OpenStreetMap/Nominatim API

The system integrates with the OpenStreetMap Nominatim API for geocoding addresses:

```python
# Geocoding address
full_address = f"{address_line}, {city}, {state} {postal_code}"

try:
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
    # Log the error and continue (geocoding is not critical)
    print(f"Geocoding error: {e}")
```

This API integration enables:
- Automatic geocoding of customer and provider addresses
- Distance-based provider matching
- Location-aware service delivery

### 6.2 Twilio API Integration for OTP Verification

The system integrates with Twilio for sending OTP verification codes:

```python
def generate_otp(phone_number):
    # Generate 6-digit OTP
    otp_code = ''.join(random.choices('0123456789', k=6))
    
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    try:
        # Format phone number to E.164 format if not already
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
            
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send OTP via SMS
        message = client.messages.create(
            body=f"Your HIRE Platform verification code is: {otp_code}",
            from_=twilio_number,
            to=phone_number
        )
        
        return otp_code, None
    
    except Exception as e:
        return None, f"Error sending OTP: {str(e)}"
```

This integration provides:
- Secure phone number verification
- Enhanced security for user accounts
- Reduced risk of fake accounts

## 7. Testing Strategy

The testing strategy focuses on ensuring the core algorithms and business logic function correctly:

### 7.1 Unit Testing

The project uses Python's unittest framework to test individual components:

```python
def test_calculate_distance(self):
    """Test the Haversine distance calculation function"""
    # Test with known coordinates
    lat1, lon1 = 53.349805, -6.26031  # Customer
    lat2, lon2 = 53.350140, -6.266155  # Provider 1
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    
    # Distance should be around 0.42 km
    self.assertAlmostEqual(distance, 0.42, delta=0.1)
```

### 7.2 Integration Testing

Integration tests ensure that different components work together correctly:

```python
def test_find_matching_providers(self):
    """Test the provider matching algorithm"""
    customer_address = Address.query.get(self.customer_address_id)
    
    # Find matching providers for plumbing
    plumbing_providers = find_matching_providers(customer_address, self.plumbing_id)
    
    # Should return both providers as they both offer plumbing
    self.assertEqual(len(plumbing_providers), 2)
    
    # Provider IDs should be in order of score (higher score first)
    self.assertEqual(plumbing_providers[0].id, self.provider1_id)
    self.assertEqual(plumbing_providers[1].id, self.provider2_id)
```

### 7.3 Testing Environment

- In-memory SQLite database for isolated testing
- Test data creation for consistent test scenarios
- Environment variables for controlling API behaviors

## 8. Security Measures

The system implements several security measures:

### 8.1 Password Hashing

User passwords are hashed using Werkzeug's security functions:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When creating a user
customer = Customer(
    # Other fields...
    password_hash=generate_password_hash(password)
)

# When verifying a password
if check_password_hash(customer.password_hash, password):
    # Password is correct
```

### 8.2 OTP Verification

Phone numbers are verified using one-time passwords:

```python
# Generate and send OTP
otp_code, error = generate_otp(phone)

# Create OTP record
otp_verification = OTPVerification(
    user_id=customer.id,
    user_type='customer',
    otp_code=otp_code,
    expires_at=otp_expiry,
    is_used=False
)

# Verify OTP
if verify_otp(user_id, entered_otp, user_type):
    # OTP is valid, mark user as verified
    user.is_verified = True

### 8.3 Input Validation

All user inputs are validated before processing:

```python
# Example of input validation
if not all([email, phone, first_name, last_name, password]):
    flash('All fields are required', 'danger')
    return render_template('customer/register.html')

# Email uniqueness check
if Customer.query.filter_by(email=email).first() or Provider.query.filter_by(email=email).first():
    flash('Email already registered', 'danger')
    return render_template('customer/register.html')
```

### 8.4 Authorization Checks

Routes check that users are authorized to access certain resources:

```python
# Check if user is authorized to view this booking
if (isinstance(user, Customer) and booking.customer_id != user.id) or \
   (isinstance(user, Provider) and booking.provider_id != user.id):
    flash('You are not authorized to view this booking', 'danger')
    return redirect(url_for('main.index'))
```

## 9. Software Engineering Practices

### 9.1 Modular Design

The application uses Flask blueprints to organize routes by functionality:

```python
# Create blueprints for different sections
main_bp = Blueprint('main', __name__)
customer_bp = Blueprint('customer', __name__, url_prefix='/customer')
provider_bp = Blueprint('provider', __name__, url_prefix='/provider')
service_bp = Blueprint('service', __name__, url_prefix='/services')
booking_bp = Blueprint('booking', __name__, url_prefix='/booking')
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# Register blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(provider_bp)
app.register_blueprint(service_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(payment_bp)
```

This modular approach makes the codebase more maintainable and scalable.

### 9.2 Separation of Concerns

The project clearly separates different concerns:
- **Routes**: Handle HTTP requests and responses
- **Models**: Define data structure and relationships
- **Services**: Implement business logic and algorithms
- **Templates**: Manage the presentation layer

### 9.3 Environment Configuration

The application uses environment variables and .env files for configuration:

```python
# Load environment variables
load_dotenv()

# Use environment variables with fallbacks
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hire-platform-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///hire.db')
```

### 9.4 Error Handling

The application implements proper error handling throughout:

```python
try:
    # Call the geocoding API
    response = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            address.latitude = float(data[0]['lat'])
            address.longitude = float(data[0]['lon'])
except Exception as e:
    # Log the error and continue (geocoding is not critical)
    print(f"Geocoding error: {e}")
```

### 9.5 Code Documentation

All functions and classes include docstrings explaining their purpose and parameters:

```python
def calculate_provider_score(provider, customer_address, service_category_id, avg_prices):
    """
    Calculate a score for a provider based on multiple factors:
    - Distance from customer (if addresses available)
    - Provider rating
    - Experience years
    - Price competitiveness
    
    Returns:
        Score from 0-100 (higher is better)
    """
```

## 10. User Interface Design

### 10.1 Template Structure

The application uses a hierarchical template structure:

```
templates/
├── base.html               # Base template with common elements
├── index.html              # Home page
├── customer/               # Customer-specific templates
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── add_address.html
├── provider/               # Provider-specific templates
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── add_service.html
├── services/               # Service-related templates
│   ├── list.html
│   └── detail.html
├── booking/                # Booking-related templates
│   ├── create.html
│   └── detail.html
└── payment/                # Payment-related templates
    └── process.html
```

### 10.2 Responsive Design

The user interface is responsive, adapting to different screen sizes using Bootstrap:

```html
<div class="row">
    <div class="col-md-8 offset-md-2">
        <!-- Content here will be 8/12 width on medium and larger screens,
             and full width on smaller screens -->
    </div>
</div>
```

### 10.3 User Experience Considerations

- **Flash Messages**: Provide feedback to users about their actions
- **Form Validation**: Client-side and server-side validation for forms
- **Intuitive Navigation**: Clear menu structure and breadcrumbs
- **Visual Hierarchy**: Important information is emphasized visually

## 11. Implementation Challenges and Solutions

### 11.1 Provider Matching Algorithm

**Challenge**: Creating an algorithm that balances multiple factors (rating, price, distance, experience) to find the best providers.

**Solution**: Implemented a weighted scoring system with the following components:
- Rating score (40% weight)
- Experience score (30% weight)
- Price competitiveness score (30% weight)
- Proximity bonus for nearby providers

### 11.2 Geocoding and Distance Calculation

**Challenge**: Converting addresses to coordinates and calculating distances efficiently.

**Solution**: 
- Integrated with OpenStreetMap/Nominatim API for geocoding
- Implemented the Haversine formula for accurate distance calculation
- Added error handling to gracefully handle geocoding failures

### 11.3 Booking State Management

**Challenge**: Managing the lifecycle of bookings with proper state transitions.

**Solution**: Implemented a state machine pattern with defined states and transitions:
- Initial state: pending
- Valid transitions: pending→confirmed→completed, pending→cancelled, confirmed→cancelled
- Each transition is validated before execution

## 12. Future Enhancements

Several enhancements could further improve the system:

### 12.1 Real-time Chat

Implement WebSocket-based chat functionality for communication between customers and providers:
```python
# Using Flask-SocketIO
@socketio.on('message')
def handle_message(data):
    recipient_id = data['recipient_id']
    sender_id = data['sender_id']
    message = data['message']
    
    # Save message to database
    new_message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=message
    )
    db.session.add(new_message)
    db.session.commit()
    
    # Emit message to recipient
    emit('new_message', {
        'sender_id': sender_id,
        'content': message,
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=recipient_id)
```

### 12.2 Calendar Integration

Allow providers to sync their availability with external calendars (Google Calendar, Outlook):
```python
def sync_google_calendar(provider_id, google_credentials):
    """Sync provider availability with Google Calendar"""
    service = build('calendar', 'v3', credentials=google_credentials)
    
    # Get events from Google Calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=datetime.utcnow().isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    
    # Update provider availability based on events
    # ...
```

### 12.3 Payment Gateway Integration

Integrate with real payment processors like Stripe or PayPal:
```python
def process_stripe_payment(booking_id, token):
    """Process payment using Stripe"""
    booking = Booking.query.get(booking_id)
    provider_category = ProviderCategory.query.filter_by(
        provider_id=booking.provider_id,
        category_id=booking.category_id
    ).first()
    
    amount = int(provider_category.price_rate * 100)  # Convert to cents
    
    try:
        # Create charge using Stripe
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description=f'HIRE Platform - Booking #{booking.id}',
            source=token
        )
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            amount=provider_category.price_rate,
            payment_method='credit_card',
            transaction_id=charge.id,
            status='successful'
        )
        db.session.add(payment)
        
        # Update booking status
        booking.status = 'confirmed'
        db.session.commit()
        
        return True, None
    except stripe.error.StripeError as e:
        return False, str(e)
```

## 13. Conclusion

The HIRE platform demonstrates the application of advanced programming techniques to solve real-world problems in the home service sector. By implementing sophisticated algorithms, data structures, and software engineering practices, we've created a scalable and maintainable system that effectively connects customers with qualified service providers.

Key accomplishments include:
- Implementation of a multi-factor provider matching algorithm
- Creation of a booking system with state machine pattern
- Integration with external APIs for geocoding and OTP verification
- Development of a comprehensive test suite
- Implementation of a modular, layered architecture

This project showcases how modern software development practices can be applied to create a practical, user-friendly application that addresses genuine market needs.