from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from models import Provider, ProviderCategory, Address

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r

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
    score = 0
    
    # 1. Rating score (max 40 points)
    if provider.avg_rating:
        # Convert 1-5 rating to 0-40 scale
        rating_score = (provider.avg_rating / 5) * 40
        score += rating_score
    else:
        # If no ratings yet, assign average rating score
        score += 20
    
    # 2. Experience score (max 30 points)
    # 0 years -> 0 points, 10+ years -> 30 points
    experience_score = min(30, provider.experience_years * 3)
    score += experience_score
    
    # 3. Price competitiveness (max 30 points)
    provider_category = ProviderCategory.query.filter_by(
        provider_id=provider.id,
        category_id=service_category_id
    ).first()
    
    if provider_category and service_category_id in avg_prices:
        avg_price = avg_prices[service_category_id]
        if avg_price > 0:
            # If price is below average, higher score
            price_ratio = provider_category.price_rate / avg_price
            if price_ratio < 1:
                price_score = 30 * (1 - price_ratio/2)  # Lower prices get higher scores
            else:
                price_score = max(0, 30 * (2 - price_ratio))  # Higher prices get lower scores
            
            score += price_score
    
    # Calculate distance score if addresses are available
    if customer_address and customer_address.latitude and customer_address.longitude:
        provider_address = Address.query.filter_by(provider_id=provider.id).first()
        
        if provider_address and provider_address.latitude and provider_address.longitude:
            distance = calculate_distance(
                customer_address.latitude, customer_address.longitude,
                provider_address.latitude, provider_address.longitude
            )
            
            # Distance factor: closer providers get a bonus
            if distance < 5:  # Within 5km
                score += 15
            elif distance < 10:  # Within 10km
                score += 10
            elif distance < 20:  # Within 20km
                score += 5
    
    return score

def find_matching_providers(customer_address, service_category_id, limit=5):
    """
    Find the best matching providers for a service request using our scoring algorithm
    
    Args:
        customer_address: Address object for the customer location
        service_category_id: ID of the requested service category
        limit: Maximum number of providers to return
        
    Returns:
        List of Provider objects, sorted by matching score
    """
    # Get all providers for this service category who are verified and available
    provider_categories = ProviderCategory.query.filter_by(category_id=service_category_id).all()
    if not provider_categories:
        return []
    
    # Get provider IDs
    provider_ids = [pc.provider_id for pc in provider_categories]
    
    # Get providers
    providers = Provider.query.filter(
        Provider.id.in_(provider_ids),
        Provider.is_available == True,
        Provider.is_verified == True
    ).all()
    
    if not providers:
        return []
    
    # Calculate average price per category for price competitiveness scoring
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
            provider, 
            customer_address, 
            service_category_id,
            avg_prices
        )
        provider_scores.append((provider, score))
    
    # Sort by score in descending order
    provider_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top matching providers
    return [p[0] for p in provider_scores[:limit]]

def generate_otp(phone_number):
    """
    Generate and send OTP via Twilio API
    
    Args:
        phone_number: User's phone number
        
    Returns:
        (otp_code, error) tuple
        otp_code: Generated OTP code if successful, None otherwise
        error: Error message if OTP sending failed, None otherwise
    """
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    import os
    import random
    
    # Generate 6-digit OTP
    otp_code = ''.join(random.choices('0123456789', k=6))
    
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not account_sid or not auth_token or not twilio_number:
        return None, "Twilio credentials not properly configured"
    
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
    
    except TwilioRestException as e:
        return None, f"Error sending OTP: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def verify_otp(user_id, entered_otp, user_type='customer'):
    """
    Verify OTP code from database
    
    Args:
        user_id: User ID
        entered_otp: OTP entered by user
        user_type: Type of user ('customer' or 'provider')
        
    Returns:
        True if OTP is valid, False otherwise
    """
    from models import OTPVerification
    from datetime import datetime
    
    if not entered_otp or not user_id:
        return False
    
    # Get the latest OTP for this user
    otp_record = OTPVerification.query.filter_by(
        user_id=user_id,
        user_type=user_type,
        is_used=False
    ).order_by(OTPVerification.created_at.desc()).first()
    
    if not otp_record:
        return False
    
    # Check if OTP matches
    if entered_otp != otp_record.otp_code:
        return False
    
    # Check if OTP is expired
    if datetime.utcnow() > otp_record.expires_at:
        return False
    
    # Mark OTP as used
    otp_record.is_used = True
    from app import db
    db.session.commit()
    
    return True