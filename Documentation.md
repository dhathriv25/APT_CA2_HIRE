# HIRE Platform - System Documentation

## 1. Introduction

The HIRE platform is an information system designed to connect residential service customers with qualified service providers for household maintenance services. It addresses the challenge of finding trusted professionals for home services while also providing service providers with a platform to showcase their skills and find clients.

## 2. Problem Domain Analysis

The home service sector faces several challenges:

- **For Customers**: Finding reliable, qualified professionals for home maintenance is time-consuming and often relies on word-of-mouth recommendations.
- **For Service Providers**: Skilled professionals struggle to find consistent work opportunities and have limited ability to market themselves effectively.

HIRE solves these problems by creating a digital marketplace with:
- Verified provider profiles with transparent ratings
- Easy booking and scheduling system
- Secure payment processing
- Location-based provider matching

## 3. System Architecture

### 3.1 Architectural Pattern

The HIRE platform follows a **layered architecture pattern** with clear separation of concerns:

1. **Presentation Layer**: Flask routes and Jinja2 templates handling the user interface
2. **Business Logic Layer**: Services module containing algorithms and business rules
3. **Data Access Layer**: SQLAlchemy models for database interactions

This architecture provides several benefits:
- **Maintainability**: Changes to one layer don't affect others
- **Testability**: Each layer can be tested independently
- **Scalability**: Layers can be scaled horizontally if needed

### 3.2 Technologies Used

- **Backend Framework**: Flask - A lightweight Python web framework
- **Database**: SQLite (can be migrated to SQL Server)
- **ORM**: SQLAlchemy - Provides an abstraction over the database
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **API Integration**: OpenStreetMap/Nominatim for geocoding

## 4. Data Structures and Algorithms

### 4.1 Data Models

The system uses the following key data structures:

#### 4.1.1 Core Models

1. **Customer**: Represents end users who book services
   ```python
   class Customer(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(100), unique=True, nullable=False)
       # Other fields...
       addresses = db.relationship('Address', backref='customer', lazy=True)
       bookings = db.relationship('Booking', backref='customer', lazy=True)
   ```

2. **Provider**: Represents service professionals
   ```python
   class Provider(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       # Fields...
       services = db.relationship('ProviderCategory', backref='provider', lazy=True)
       bookings = db.relationship('Booking', backref='provider', lazy=True)
   ```

3. **Booking**: Implements a state machine for tracking service bookings
   ```python
   class Booking(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       # Relationships and fields...
       status = db.Column(db.String(20), default='pending', nullable=False)
       # Possible states: pending, confirmed, completed, cancelled
   ```

#### 4.1.2 Relationship Models

1. **ProviderCategory**: Many-to-many relationship between providers and service categories with additional pricing information
   ```python
   class ProviderCategory(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
       category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
       price_rate = db.Column(db.Float, nullable=False)
   ```

2. **Address**: Stores geographical location information with latitude and longitude for distance calculations
   ```python
   class Address(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       # Fields...
       latitude = db.Column(db.Float, nullable=True)
       longitude = db.Column(db.Float, nullable=True)
   ```

### 4.2 Key Algorithms

#### 4.2.1 Provider Matching Algorithm

The provider matching algorithm (`find_matching_providers()`) is a core component that finds the most suitable service providers for a customer based on multiple factors:

```python
def find_matching_providers(customer_address, service_category_id, limit=5):
    # Get providers for this category who are verified and available
    # Calculate scores for each provider
    # Return top matches
```

The scoring algorithm uses weighted criteria:
- **Provider Rating (40%)**: Higher-rated providers receive more points
- **Experience Years (30%)**: More experienced providers get higher scores
- **Price Competitiveness (30%)**: Providers charging less than average get bonus points
- **Proximity Bonus**: Providers closer to the customer's location receive additional points

This multi-criteria approach ensures customers get high-quality, reasonably priced service providers who are nearby.

#### 4.2.2 Haversine Distance Calculation

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
- The Haversine formula for spherical distance
- Coordinate system transformation

#### 4.2.3 Booking State Machine

The Booking model implements a finite state machine pattern for tracking the lifecycle of service bookings:

- **Initial State**: `pending` (booking created but not paid)
- **Valid Transitions**:
  - `pending` → `confirmed` (after payment)
  - `pending` → `cancelled` (customer cancels)
  - `confirmed` → `completed` (service performed)
  - `confirmed` → `cancelled` (customer or provider cancels)

This pattern encapsulates booking state logic and ensures only valid state transitions are allowed.

## 5. API Integration

### 5.1 OpenStreetMap/Nominatim API

The system integrates with the OpenStreetMap Nominatim API for geocoding addresses:

```python
# Geocoding address
params = {
    'q': full_address,
    'format': 'json',
    'limit': 1
}
response = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers)
if response.status_code == 200:
    data = response.json()
    if data:
        address.latitude = float(data[0]['lat'])
        address.longitude = float(data[0]['lon'])
```

This API integration enables:
- Automatic geocoding of customer and provider addresses
- Distance-based provider matching
- Location-aware service delivery

## 6. Testing Strategy

The testing strategy focuses on ensuring the core algorithms function correctly:

1. **Unit Testing**: Testing individual functions and methods
   ```python
   def test_calculate_distance():
       # Test the distance calculation between two known points
       distance = calculate_distance(53.349805, -6.26031, 53.350140, -6.266155)
       assert round(distance, 2) == 0.42  # 0.42 km between points
   ```

2. **Integration Testing**: Testing the interaction between components
   ```python
   def test_provider_matching():
       # Test that provider matching returns appropriate results
       providers = find_matching_providers(customer_address, service_category_id)
       assert len(providers) <= 5  # Should return maximum 5 providers
       # Check providers are sorted by score
   ```

## 7. Security Considerations

The system implements several security measures:

1. **Password Hashing**: User passwords are hashed using Werkzeug's security functions
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   
   # When creating a user
   password_hash = generate_password_hash(password)
   
   # When verifying a password
   check_password_hash(user.password_hash, password)
   ```

2. **CSRF Protection**: Forms include CSRF tokens to prevent cross-site request forgery
3. **Input Validation**: All user inputs are validated before processing
4. **Phone Verification**: OTP verification for user phone numbers

## 8. Future Enhancements

Several enhancements could further improve the system:

1. **Real-time Chat**: Implement WebSocket-based chat between customers and providers
2. **Calendar Integration**: Allow providers to sync their availability with external calendars
3. **Payment Gateway Integration**: Integrate with real payment processors
4. **Machine Learning**: Implement ML-based provider recommendations based on user preferences
5. **Mobile Application**: Develop a mobile app for both customers and providers

## 9. Conclusion

The HIRE platform demonstrates the application of advanced programming techniques including:
- Complex data structures and relationships
- Algorithmic approaches to provider matching
- State machine pattern for booking lifecycle
- API integration for geocoding
- Layered architectural pattern

These technical choices enable a scalable, maintainable system that effectively connects customers with qualified service providers in the home service market.