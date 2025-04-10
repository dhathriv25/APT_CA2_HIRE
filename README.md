# HIRE Platform

HIRE is a comprehensive web application that connects residential service customers with qualified service providers for household maintenance services. The platform aims to solve the challenge of finding trusted professionals for home services while providing service providers with an effective way to showcase their skills and find clients.

## Project Overview

The HIRE platform implements a layered architecture with:

- **Presentation Layer**: Flask routes and Jinja2 templates
- **Business Logic Layer**: Services module with algorithms
- **Data Access Layer**: SQLAlchemy models

## Key Features

- User registration and profile management (customers and service providers)
- Service categorization and provider association
- Booking system with state management (pending → confirmed → completed)
- Provider matching algorithm based on rating, price, experience, and location
- Payment processing (simulated)
- Rating and review system
- Geocoding and distance-based provider search

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite (can be migrated to SQL Server)
- **ORM**: SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Template Engine**: Jinja2
- **APIs**: OpenStreetMap/Nominatim for geocoding, Twilio for OTP (optional)

## Project Structure

```
hire-platform/
├── app.py                  # Application entry point
├── models.py               # Database models
├── routes.py               # Route definitions
├── services.py             # Business logic and algorithms
├── requirements.txt        # Project dependencies
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── customer/
│   ├── provider/
│   ├── booking/
│   ├── payment/
│   └── services/
└── tests/                  # Test suite
    └── test_services.py
```

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hire-platform.git
   cd hire-platform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URI=sqlite:///hire.db
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-phone
   OTP_TEST_MODE=True
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application at [http://localhost:5000](http://localhost:5000)

## Testing

Run the tests using:
```bash
python -m unittest tests/test_services.py
```

## Core Algorithms

### Provider Matching Algorithm

The provider matching algorithm finds the most suitable service providers for a customer based on multiple factors:

- Provider rating (40%)
- Experience years (30%)
- Price competitiveness (30%)
- Proximity bonus (additional points)

### Haversine Distance Calculation

The `calculate_distance()` function implements the Haversine formula to calculate the great-circle distance between two geographical points. This is used to determine the distance between customers and providers.

### Booking State Machine

The Booking model implements a finite state machine pattern with well-defined state transitions:
- pending → confirmed → completed
- pending → cancelled
- confirmed → cancelled

## API Integrations

- **OpenStreetMap/Nominatim**: For geocoding addresses
- **Twilio API**: For sending OTP verification codes (can be run in test mode)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dublin Business School for the project requirements
- OpenStreetMap for the geocoding API
- All open-source libraries used in this project