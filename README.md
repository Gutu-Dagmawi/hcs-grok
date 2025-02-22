# Hospital Cardless System (HCS)

A modern web application that digitizes hospital patient identification and management using QR codes instead of physical cards. Built with Flask and FastHTML.

## Features

- Digital patient registration with QR code generation
- Appointment booking and management
- Mock payment integration (Telebirr and Chapa)
- Medical history tracking
- Admin dashboard with analytics
- QR code-based patient identification

## Tech Stack

- **Backend**: Flask with SQLite
- **Frontend**: FastHTML
- **Database**: SQLAlchemy ORM
- **Authentication**: Flask-Login
- **QR Code**: qrcode library
- **Charts**: Plotly
- **Form Handling**: Flask-WTF

## Project Structure

```
hcs-grok/
├── app/
│   ├── templates/          # FastHTML templates
│   ├── static/            # Static files (CSS, JS, images)
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # Route handlers
│   └── utils/            # Utility functions
├── tests/                # Test files
├── docs/                 # Documentation
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the development server:
   ```bash
   flask run
   ```

## Development Status

- [x] Project structure setup
- [x] Database models implementation
- [x] Authentication system
- [x] Patient registration
- [x] QR code generation
- [x] Base templates and layouts
- [x] Landing page
- [x] Patient dashboard
- [x] Patient profile management
- [ ] Appointment booking system
- [ ] Mock payment integration
- [ ] Doctor dashboard and availability
- [ ] Admin dashboard and management
- [ ] Analytics and reporting
- [ ] Testing and documentation

## Contributing

This is a class project demonstrating the implementation of a hospital management system. Contributions are welcome through pull requests.

## License

This project is for educational purposes only. 