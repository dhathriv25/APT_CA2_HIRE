import unittest
import os
import sys
from datetime import datetime, timedelta
from math import radians

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Customer, Provider, ServiceCategory, ProviderCategory, Address, Booking, Payment, OTPVerification
from services import calculate_distance, calculate_provider_score, find_matching_providers, generate_otp, verify_otp

class TestServices(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        # Create tables and context
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test data
        self._create_test_data()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_test_data(self):
        """Create test data for the tests"""
        # Create service categories
        plumbing = ServiceCategory(name="Plumbing", description="Plumbing services")
        electrical = ServiceCategory(name="Electrical", description="Electrical services")
        db.session.add_all([plumbing, electrical])
        db.session.commit()

        # Create providers
        provider1 = Provider(
            email="provider1@example.com",
            phone="+1234567890",
            password_hash="hash1",
            first_name="John",
            last_name="Smith",
            verification_document="doc1.pdf",
            experience_years=5,
            is_available=True,
            avg_rating=4.5,
            is_verified=True
        )
        provider2 = Provider(
            email="provider2@example.com",
            phone="+0987654321",
            password_hash="hash2",
            first_name="Jane",
            last_name="Doe",
            verification_document="doc2.pdf",
            experience_years=3,
            is_available=True,
            avg_rating=4.0,
            is_verified=True
        )
        db.session.add_all([provider1, provider2])
        db.session.commit()

        # Create provider categories (services offered by providers)
        pc1 = ProviderCategory(provider_id=provider1.id, category_id=plumbing.id, price_rate=50.0)
        pc2 = ProviderCategory(provider_id=provider2.id, category_id=plumbing.id, price_rate=45.0)
        pc3 = ProviderCategory(provider_id=provider1.id, category_id=electrical.id, price_rate=60.0)
        db.session.add_all([pc1, pc2, pc3])
        db.session.commit()

        # Create customer
        customer = Customer(
            email="customer@example.com",
            phone="+1122334455",
            password_hash="hash3",
            first_name="Alice",
            last_name="Johnson",
            is_verified=True
        )
        db.session.add(customer)
        db.session.commit()

        # Create addresses with geocoding
        customer_address = Address(
            customer_id=customer.id,
            address_line="123 Main St",
            city="Dublin",
            state="Dublin",
            postal_code="D01 AB12",
            latitude=53.349805,
            longitude=-6.26031
        )
        provider1_address = Address(
            provider_id=provider1.id,
            address_line="456 Oak Ave",
            city="Dublin",
            state="Dublin",
            postal_code="D02 CD34",
            latitude=53.350140,
            longitude=-6.266155
        )
        provider2_address = Address(
            provider_id=provider2.id,
            address_line="789 Pine St",
            city="Dublin",
            state="Dublin",
            postal_code="D03 EF56",
            latitude=53.348750,
            longitude=-6.270000
        )
        db.session.add_all([customer_address, provider1_address, provider2_address])
        db.session.commit()

        # Save IDs for use in tests
        self.plumbing_id = plumbing.id
        self.electrical_id = electrical.id
        self.provider1_id = provider1.id
        self.provider2_id = provider2.id
        self.customer_id = customer.id
        self.customer_address_id = customer_address.id

    def test_calculate_distance(self):
        """Test the Haversine distance calculation function"""
        # Test with known coordinates
        lat1, lon1 = 53.349805, -6.26031  # Customer
        lat2, lon2 = 53.350140, -6.266155  # Provider 1
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        
        # Distance should be around 0.42 km
        self.assertAlmostEqual(distance, 0.42, delta=0.1)
        
        # Test with provider 2 (should be farther)
        lat3, lon3 = 53.348750, -6.270000  # Provider 2
        distance2 = calculate_distance(lat1, lon1, lat3, lon3)
        self.assertGreater(distance2, distance)

    def test_calculate_provider_score(self):
        """Test the provider scoring algorithm"""
        customer_address = Address.query.get(self.customer_address_id)
        provider1 = Provider.query.get(self.provider1_id)
        provider2 = Provider.query.get(self.provider2_id)
        
        # Create average prices dictionary
        avg_prices = {self.plumbing_id: 47.5}  # Average of 50 and 45
        
        # Calculate scores
        score1 = calculate_provider_score(provider1, customer_address, self.plumbing_id, avg_prices)
        score2 = calculate_provider_score(provider2, customer_address, self.plumbing_id, avg_prices)
        
        # Provider 1 has better rating and more experience but higher price
        # Provider 2 has lower rating and less experience but lower price
        # The scores should reflect this combination of factors
        self.assertIsInstance(score1, (int, float))
        self.assertIsInstance(score2, (int, float))
        
        # Test relative scores - the exact numbers may vary but provider 1 should score higher
        # due to higher experience and rating despite slightly higher price
        self.assertGreater(score1, score2)

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
        
        # Find matching providers for electrical
        electrical_providers = find_matching_providers(customer_address, self.electrical_id)
        
        # Should return only provider 1 as provider 2 doesn't offer electrical services
        self.assertEqual(len(electrical_providers), 1)
        self.assertEqual(electrical_providers[0].id, self.provider1_id)

    def test_generate_otp(self):
        """Test OTP generation"""
        # Set OTP_TEST_MODE for testing
        os.environ['OTP_TEST_MODE'] = 'True'
        
        # Generate OTP
        otp_code, error = generate_otp("+1122334455")
        
        # Check that an OTP was generated
        self.assertIsNotNone(otp_code)
        self.assertIsNone(error)
        self.assertEqual(len(otp_code), 6)
        self.assertTrue(otp_code.isdigit())
        
        # Check with invalid phone format
        os.environ.pop('OTP_TEST_MODE')  # Test actual behavior
        otp_code, error = generate_otp("invalid_phone")
        self.assertIsNone(otp_code)
        self.assertIsNotNone(error)

    def test_verify_otp(self):
        """Test OTP verification"""
        # Create an OTP record
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        otp_verification = OTPVerification(
            user_id=self.customer_id,
            user_type='customer',
            otp_code='123456',
            expires_at=otp_expiry
        )
        db.session.add(otp_verification)
        db.session.commit()
        
        # Test valid OTP
        self.assertTrue(verify_otp(self.customer_id, '123456', 'customer'))
        
        # Test invalid OTP
        self.assertFalse(verify_otp(self.customer_id, '654321', 'customer'))
        
        # Test expired OTP
        expired_otp = OTPVerification(
            user_id=self.customer_id,
            user_type='customer',
            otp_code='789012',
            expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        db.session.add(expired_otp)
        db.session.commit()
        self.assertFalse(verify_otp(self.customer_id, '789012', 'customer'))
        
        # Test OTP already used
        used_otp = OTPVerification(
            user_id=self.customer_id,
            user_type='customer',
            otp_code='345678',
            expires_at=otp_expiry,
            is_used=True
        )
        db.session.add(used_otp)
        db.session.commit()
        self.assertFalse(verify_otp(self.customer_id, '345678', 'customer'))

if __name__ == '__main__':
    unittest.main()