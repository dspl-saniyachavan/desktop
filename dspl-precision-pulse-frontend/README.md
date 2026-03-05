# PrecisionPulse Frontend

Real-time telemetry monitoring dashboard built with Next.js and TypeScript.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:3000 and login with:
- Admin: `admin@precisionpulse.com` / `admin123`
- User: `user@precisionpulse.com` / `user123`

## What's Inside

This is a web dashboard for monitoring telemetry data in real-time. It connects to desktop applications via WebSocket and displays live sensor readings with charts.

### Main Features

- Live telemetry streaming (updates every 3 seconds)
- User authentication with JWT
- Admin panel for managing users and parameters
- Real-time charts showing 60-second history
- Role-based permissions (admin vs regular user)

### Tech Used

- Next.js 16 with React 19
- TypeScript
- Tailwind CSS for styling
- Socket.io and MQTT for real-time data
- bcrypt for password security

## Project Layout

```
src/
├── app/
│   ├── api/auth/       - Login/auth endpoints
│   ├── dashboard/      - Main telemetry view
│   ├── login/          - Login page
│   ├── parameters/     - Admin: configure sensors
│   ├── profile/        - User settings
│   └── users/          - Admin: user management
├── components/
│   ├── ui/             - Buttons, inputs, etc.
│   ├── ProtectedRoute.tsx
│   └── RBACGuard.tsx
├── models/             - TypeScript types
└── services/           - Business logic
```

## Environment Setup

Create `.env.local` from the example file:

```bash
cp .env.example .env.local
```

Or manually create `.env.local` with:

```
JWT_SECRET=precision-pulse-super-secret-jwt-key-2024-development-only
NEXT_PUBLIC_API_URL=http://localhost:3000
```

**Important**: Never commit `.env.local` to git. It's already in `.gitignore`.

## How It Works

The dashboard connects to a desktop application that collects sensor data. Admins can configure which parameters to monitor through the Parameters page. The desktop app reads this config and sends only enabled parameters via WebSocket.

Regular users can view the dashboard and their profile. Admins get additional access to user management and parameter configuration.

## Development

```bash
npm run dev      # Development server
npm run build    # Production build
npm start        # Run production build
npm run lint     # Check code
```

## Notes

- Passwords must have uppercase, lowercase, and numbers
- JWT tokens expire after 24 hours
- Parameter changes sync automatically with connected desktop apps
- Charts show last 20 data points (60 seconds)

## Requirements

- Node.js 20 or higher
- Modern browser (Chrome, Firefox, Safari, Edge)

## License

Private project - not for public distribution.
