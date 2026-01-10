# Campus Wallet System

## Overview

Campus Wallet System is a digital payment platform designed specifically for educational institutions. The application enables students to load money into their digital wallets and make QR code-based payments to campus vendors such as cafeterias, bookstores, and other campus services. The system supports three user roles: students who can load money and make payments, vendors who can generate QR codes and receive payments, and administrators who can monitor the overall system.

The platform provides a comprehensive transaction management system with real-time balance tracking, payment history, and QR code generation for seamless campus-wide digital transactions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses a traditional server-rendered architecture built with Flask and Jinja2 templates. The frontend employs Bootstrap 5 for responsive UI components and Font Awesome for icons. The template structure follows a base template pattern with role-specific dashboards (student, vendor, admin) that extend the base layout. Navigation is dynamically rendered based on user authentication status and role permissions.

### Backend Architecture
The backend is built on Flask with a modular structure separating route handlers from data models. The application uses Flask-Login for session management and user authentication, providing secure login/logout functionality with password hashing via Werkzeug. CORS support is enabled for potential future API integrations.

The main application logic is centralized in `main.py` with database models defined in `models.py`. User roles are enforced through template-level conditional rendering and route-based access control.

### Data Storage Solutions
The application uses SQLAlchemy ORM with support for multiple database backends through environment-based configuration. The database schema includes five core entities:

- **Users**: Stores user credentials, personal information, and role assignments
- **Wallets**: Manages user account balances with one-to-one relationship to users
- **Vendors**: Contains vendor-specific information like shop names and types
- **Transactions**: Records all financial activities with sender/receiver relationships
- **QRCodes**: Manages QR code generation and validation for payments

The schema uses foreign key relationships to maintain data integrity and supports transaction history tracking.

### Authentication and Authorization
Authentication is handled through Flask-Login with session-based user management. Passwords are securely hashed using Werkzeug's security utilities. The system implements a role-based access control system with three distinct roles:

- **Students**: Can load money, make payments via QR codes, and view transaction history
- **Vendors**: Can generate payment QR codes, receive payments, and manage shop information
- **Administrators**: Have system-wide visibility and can monitor all users and transactions

Role-based navigation and feature access are enforced at the template level, with different dashboard views for each user type.

### Payment Processing Architecture
The payment system operates through QR code-based transactions. Vendors can generate unique QR codes containing payment information, which students can scan to initiate payments. The system processes transactions by validating QR codes, checking wallet balances, and updating both sender and receiver accounts atomically.

Transaction records maintain complete audit trails with unique transaction IDs, timestamps, and status tracking. The system supports both money loading (credit) and payment (debit) transaction types.

## External Dependencies

### Web Framework and Extensions
- **Flask**: Core web framework for handling HTTP requests and routing
- **Flask-Login**: User session management and authentication
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-SQLAlchemy**: Database ORM integration

### Database Technology
- **SQLAlchemy**: Object-relational mapping and database abstraction
- **Database Backend**: Configurable through DATABASE_URL environment variable (supports PostgreSQL, MySQL, SQLite)

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive UI components
- **Font Awesome 6**: Icon library for user interface elements

### Security and Utilities
- **Werkzeug Security**: Password hashing and verification utilities
- **Python QRCode**: QR code generation library for payment processing
- **Base64 Encoding**: Image encoding for QR code display in templates

### Environment Configuration
The application relies on environment variables for sensitive configuration:
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string

No external payment gateways or third-party financial services are currently integrated, making this a self-contained campus payment ecosystem.