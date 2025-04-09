from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hire-platform-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///hire.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models after initializing db
from models import Customer, Provider, ServiceCategory, ProviderCategory, Address, Booking, Payment, OTPVerification

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Add initial service categories if none exist
    if ServiceCategory.query.count() == 0:
        categories = [
            ServiceCategory(name="Plumbing", description="All plumbing services including repairs, installations, and maintenance"),
            ServiceCategory(name="Electrical", description="Electrical repairs, installations, and maintenance services"),
            ServiceCategory(name="Cleaning", description="Professional home cleaning services including regular cleaning, deep cleaning, and specialized cleaning"),
            ServiceCategory(name="Carpentry", description="Woodwork, furniture repairs, and custom woodworking services"),
            ServiceCategory(name="Painting", description="Interior and exterior painting services for homes and businesses"),
            ServiceCategory(name="Landscaping", description="Garden maintenance, lawn care, and landscaping design services"),
            ServiceCategory(name="HVAC", description="Heating, ventilation, and air conditioning installation and repairs")
        ]
        db.session.add_all(categories)
        db.session.commit()

# Register blueprints
from routes import main_bp, customer_bp, provider_bp, service_bp, booking_bp, payment_bp

app.register_blueprint(main_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(provider_bp)
app.register_blueprint(service_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(payment_bp)

if __name__ == '__main__':
    app.run(debug=True)