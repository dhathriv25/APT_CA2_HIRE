from datetime import datetime
from db_setup import db 

class Customer(db.Model):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    addresses = db.relationship('Address', backref='customer', lazy=True, 
                              foreign_keys='Address.customer_id')
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    
    def get_full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Customer {self.email}>"


class Provider(db.Model):
    """Provider model"""
    __tablename__ = 'providers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    verification_document = db.Column(db.String(255), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    avg_rating = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    addresses = db.relationship('Address', backref='provider', lazy=True, 
                              foreign_keys='Address.provider_id')
    services = db.relationship('ProviderCategory', backref='provider', lazy=True)
    bookings = db.relationship('Booking', backref='provider', lazy=True)
    
    def get_full_name(self):
        """Return provider's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Provider {self.email}>"

class ServiceCategory(db.Model):
    """Service category model"""
    __tablename__ = 'service_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<ServiceCategory {self.name}>"

class ProviderCategory(db.Model):
    """Provider-category association with pricing"""
    __tablename__ = 'provider_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    price_rate = db.Column(db.Float, nullable=False)
    
    # Relationship
    category = db.relationship('ServiceCategory', backref='provider_categories')
    
    __table_args__ = (
        db.UniqueConstraint('provider_id', 'category_id', name='uq_provider_category'),
    )
    
    def __repr__(self):
        return f"<ProviderCategory provider_id={self.provider_id} category_id={self.category_id}>"

class Address(db.Model):
    """Address model with geocoding"""
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=True)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='address', lazy=True)
    
    def get_full_address(self):
        """Return the full formatted address"""
        return f"{self.address_line}, {self.city}, {self.state} {self.postal_code}"
    
    def __repr__(self):
        if self.customer_id:
            return f"<Address (Customer {self.customer_id}): {self.get_full_address()}>"
        else:
            return f"<Address (Provider {self.provider_id}): {self.get_full_address()}>"

class Booking(db.Model):
    """Booking model with state machine"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    
    # Booking details
    booking_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # State machine: booking status
    # pending -> confirmed -> completed
    # pending -> cancelled
    # confirmed -> cancelled
    STATUS_CHOICES = ['pending', 'confirmed', 'completed', 'cancelled']
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Rating (1-5 stars, only filled after service completion)
    rating = db.Column(db.Integer, nullable=True)
    rating_comment = db.Column(db.Text, nullable=True)
    
    # Relationships
    payment = db.relationship('Payment', backref='booking', lazy=True, uselist=False)
    category = db.relationship('ServiceCategory')
    
    def __repr__(self):
        return f"<Booking {self.id} status={self.status}>"

class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    
    # Payment method
    PAYMENT_METHOD_CHOICES = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
    payment_method = db.Column(db.String(50), nullable=False)
    
    # Transaction details
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # Payment status
    STATUS_CHOICES = ['pending', 'successful', 'failed', 'refunded']
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment {self.id} status={self.status}>"

class OTPVerification(db.Model):
    """OTP Verification model"""
    __tablename__ = 'otp_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'customer' or 'provider'
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<OTPVerification for {self.user_type} {self.user_id}>"