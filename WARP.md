# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is the **Denew Backend** - a Django REST API that powers a VIP task completion and financial management platform. The application handles user authentication, task systems, financial transactions (deposits/withdrawals), and referral programs.

## Architecture

### Core Components

**User Management & Authentication**
- Custom User model extending AbstractUser with VIP levels, balances, and referral codes
- JWT-based authentication using Simple JWT
- Profile management with withdrawal PIN security
- User registration includes automatic $50 bonus and referral code generation

**Task System**
- VIP-based task allocation with earnings based on user level
- Set-based task progression (users complete tasks in sequential sets)
- Combined tasks for higher VIP levels with higher earnings
- Task status tracking: pending → in-progress → completed

**Financial Operations**
- Deposit/Withdrawal management with USDT as primary payment method
- Balance tracking and automatic earnings credit
- Withdrawal PIN security for financial operations
- Transaction history and portfolio management

**Referral & Invitation System**
- User referral codes and invitation tracking
- Campaign management for promotional activities

**Support & Administration**
- Support ticket system with priority levels
- Admin controls for withdrawal approvals
- Terms and conditions management

### Key Models
- `User`: Extended user model with balance, VIP level, referral system
- `Task`: Task assignments with products, earnings, and status tracking  
- `Product`: Products associated with tasks (pricing, icons, combined status)
- `Deposit`/`Withdrawal`: Financial transaction records
- `Campaign`: Marketing campaigns and promotional activities
- `SupportTicket`: Customer support ticket management

### API Structure
All API endpoints are under `/api/` with JWT authentication:
- Authentication: `/api/register/`, `/api/login/`, `/api/logout/`
- User Management: `/api/profile/`, `/api/dashboard/`
- Tasks: `/api/tasks/`, `/api/tasks/current/`, `/api/tasks/start-set/`
- Financial: `/api/deposit/`, `/api/withdrawal/`, `/api/transactions/`
- Social: `/api/invite/`, `/api/campaigns/`

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Database setup (PostgreSQL)
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 0.0.0.0:8000
```

### Database Management
```bash
# Create new migrations
python manage.py makemigrations
python manage.py makemigrations accounts

# Apply migrations
python manage.py migrate

# Reset database (custom script)
python reset_db.py

# Update user balance (custom script)
python update_balance.py
```

### Testing
```bash
# Run Django tests
python manage.py test

# Run specific app tests
python manage.py test denew_backend.accounts

# API testing script
python test_task_system.py
```

### Database Shell & Management
```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic
```

### Deployment Preparation
```bash
# Check deployment readiness
python manage.py check --deploy

# Create production static files
python manage.py collectstatic --noinput
```

## Configuration

### Environment Variables
Key environment variables used in `settings.py`:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (default: True)
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS
- `EMAIL_HOST_USER`: Gmail SMTP username
- `EMAIL_HOST_PASSWORD`: Gmail app password

### Database Configuration
- **Development**: PostgreSQL with user `denew_user`, database `denew_db`
- **Production**: Uses `DATABASE_URL` environment variable
- Custom user model: `accounts.User`

### Key Settings
- **Time Zone**: `Africa/Lagos`
- **JWT Token Lifetime**: 60 minutes (access), 1 day (refresh)
- **Password Validation**: Minimum 6 characters
- **Withdrawal PIN**: 4-digit numeric requirement

## Production Deployment

The application is configured for **Render.com** deployment with:
- WhiteNoise for static file serving
- Gunicorn as WSGI server
- PostgreSQL database
- CORS configured for frontend at `denew-hub.com`
- Security headers enabled in production mode

### Security Features
- JWT token blacklisting on logout
- CORS protection with specific origin allowlist
- Withdrawal PIN protection for financial operations
- HTTPS redirect and security headers in production
- Custom middleware for operating hours (9:00-21:59)

## Testing Strategy

- **Unit Tests**: Basic Django test framework setup in each app
- **API Testing**: Custom integration test script (`test_task_system.py`) 
- **Manual Testing**: Tests full user flow from registration to task completion

The test script covers:
1. User registration/login flow
2. Profile management
3. Task system (start set → get current task → complete task)
4. Dashboard data retrieval

## File Structure Notes

```
denew_backend/
├── accounts/          # Main app (users, tasks, transactions)
├── core/              # Additional app (minimal usage)
├── settings.py        # Django configuration
├── urls.py           # URL routing
├── middleware.py     # Operating hours middleware
└── wsgi.py/asgi.py   # Server configuration
```

The `accounts` app contains the majority of business logic, with comprehensive models, serializers, and views handling all core platform functionality.
