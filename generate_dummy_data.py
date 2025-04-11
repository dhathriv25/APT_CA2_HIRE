from datetime import datetime, timedelta
import random
from faker import Faker
from models import db, Customer, Provider, ServiceCategory, ProviderCategory, Address, Booking, Payment, OTPVerification

fake = Faker()

# Service categories
service_categories = [
    "Plumbing",
    "Electrical",
    "Cleaning",
    "Gardening",
    "Painting",
    "Carpentry",
    "Moving",
    "Appliance Repair"
]

def create_customers(count=5):
    """Generate dummy customers"""
    customers = []
    for _ in range(count):
        customer = Customer(
            email=fake.email(),
            phone=fake.phone_number(),
            password_hash="$2b$12$EixZaYVK1fsbY1eIYhQ3h.ihI9fhIvjZvJ/vJYrJXpIr8qz5ELu.",  # 'password'
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_verified=True  # Always set to True
        )
        db.session.add(customer)
        customers.append(customer)
    db.session.commit()
    print("\nCustomer login credentials:")
    for customer in customers:
        print(f"Email: {customer.email}, Password: password")
    return customers

def create_providers(count=5):
    """Generate dummy providers"""
    providers = []
    for _ in range(count):
        provider = Provider(
            email=fake.email(),
            phone=fake.phone_number(),
            password_hash="$2b$12$EixZaYVK1fsbY1eIYhQ3h.ihI9fhIvjZvJ/vJYrJXpIr8qz5ELu.",  # 'password'
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            verification_document="document.jpg",
            experience_years=random.randint(1, 20),
            is_available=random.choice([True, False]),
            avg_rating=round(random.uniform(1, 5), 1) if random.choice([True, False]) else None,
            is_verified=True  # Always set to True
        )
        db.session.add(provider)
        providers.append(provider)
    db.session.commit()
    print("\nProvider login credentials:")
    for provider in providers:
        print(f"Email: {provider.email}, Password: password")
    return providers

def create_service_categories():
    """Generate service categories"""
    categories = []
    for name in service_categories:
        category = ServiceCategory(
            name=name,
            description=f"Professional {name.lower()} services"
        )
        db.session.add(category)
        categories.append(category)
    db.session.commit()
    return categories

def create_provider_services(providers, categories):
    """Associate providers with services"""
    provider_services = []
    for provider in providers:
        for category in random.sample(categories, random.randint(1, 3)):
            pc = ProviderCategory(
                provider_id=provider.id,
                category_id=category.id,
                price_rate=round(random.uniform(20, 200), 2)
            )
            db.session.add(pc)
            provider_services.append(pc)
    db.session.commit()
    return provider_services

def create_addresses(customers, providers):
    """Generate addresses for customers and providers"""
    addresses = []
    
    # Customer addresses
    for customer in customers:
        for _ in range(random.randint(1, 3)):
            address = Address(
                customer_id=customer.id,
                address_line=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                postal_code=fake.postcode(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude())
            )
            db.session.add(address)
            addresses.append(address)
    
    # Provider addresses
    for provider in providers:
        address = Address(
            provider_id=provider.id,
            address_line=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.postcode(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude())
        )
        db.session.add(address)
        addresses.append(address)
    
    db.session.commit()
    return addresses

def create_bookings(customers, providers, categories, addresses):
    """Generate bookings"""
    bookings = []
    statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    time_slots = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
    
    for customer in customers:
        customer_addresses = [a for a in addresses if a.customer_id == customer.id]
        if not customer_addresses:
            continue
            
        for _ in range(random.randint(1, 5)):
            provider = random.choice(providers)
            provider_categories = ProviderCategory.query.filter_by(provider_id=provider.id).all()
            if not provider_categories:
                continue
                
            category = random.choice(provider_categories).category
            address = random.choice(customer_addresses)
            
            # Random date in next 30 days
            booking_date = datetime.utcnow().date() + timedelta(days=random.randint(1, 30))
            
            booking = Booking(
                customer_id=customer.id,
                provider_id=provider.id,
                category_id=category.id,
                address_id=address.id,
                booking_date=booking_date,
                time_slot=random.choice(time_slots),
                status=random.choice(statuses),
                rating=random.randint(1, 5) if random.choice([True, False]) else None,
                rating_comment=fake.sentence() if random.choice([True, False]) else None
            )
            db.session.add(booking)
            bookings.append(booking)
    
    db.session.commit()
    return bookings

def create_payments(bookings):
    """Generate payments for bookings"""
    payments = []
    methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
    statuses = ['pending', 'successful', 'failed', 'refunded']
    
    for booking in bookings:
        if booking.status in ['confirmed', 'completed']:
            provider_category = ProviderCategory.query.filter_by(
                provider_id=booking.provider_id,
                category_id=booking.category_id
            ).first()
            
            if provider_category:
                payment = Payment(
                    booking_id=booking.id,
                    amount=provider_category.price_rate,
                    payment_method=random.choice(methods),
                    transaction_id=fake.uuid4(),
                    status=random.choice(statuses)
                )
                db.session.add(payment)
                payments.append(payment)
    
    db.session.commit()
    return payments

def generate_dummy_data():
    """Main function to generate all dummy data"""
    print("Generating dummy data...")
    
    # Clear existing data
    print("Clearing existing data...")
    db.drop_all()
    db.create_all()
    
    # Create data
    print("Creating customers...")
    customers = create_customers()
    
    print("Creating providers...")
    providers = create_providers()
    
    print("Creating service categories...")
    categories = create_service_categories()
    
    print("Creating provider services...")
    provider_services = create_provider_services(providers, categories)
    
    print("Creating addresses...")
    addresses = create_addresses(customers, providers)
    
    print("Creating bookings...")
    bookings = create_bookings(customers, providers, categories, addresses)
    
    print("Creating payments...")
    payments = create_payments(bookings)
    
    print("Dummy data generation complete!")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        generate_dummy_data()