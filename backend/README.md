# PrecisionPulse Backend

Flask backend with SQLAlchemy, JWT authentication.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run server:
```bash
python3 run.py
```

Server runs on `http://localhost:5001`

## API Endpoints

- `POST /api/auth/login` - Login with email and password
- `POST /api/auth/register` - Register new user
