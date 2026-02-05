# CryptoFlyt 🚀

A real-time cryptocurrency dashboard with price alerts, portfolio tracking, and AI-powered market analysis.

![17703277414995708817871352985069](https://github.com/user-attachments/assets/44eadab0-a908-4cab-8aac-6522dacd4d74)


## Features

- 📈 **Real-time Prices** - Live streaming from Bybit WebSocket
- 🔔 **Price Alerts** - Get notified when prices hit your targets
- 💼 **Portfolio Tracking** - Track holdings and P&L
- 🤖 **AI Analysis** - Market insights powered by Google Gemini
- 📱 **Telegram Notifications** - Alerts sent to your phone
- 🔐 **User Authentication** - JWT-based secure login

## Tech Stack

**Backend:**
- Python FastAPI
- PostgreSQL + SQLAlchemy
- Redis + Celery (background tasks)
- Bybit WebSocket API
- Google Gemini AI

**Frontend:**
- React 18
- Tailwind CSS
- Recharts (charts)
- Zustand (state management)
- React Router

**Infrastructure:**
- Docker Compose
- Nginx (optional)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### 1. Clone and configure

```bash
cd cryptoflyt
cp .env.example .env
```

Edit `.env` to add your API keys (optional):
- `GOOGLE_API_KEY` - For AI market analysis
- `TELEGRAM_BOT_TOKEN` - For Telegram notifications

### 2. Start the application

```bash
docker-compose up --build
```

### 3. Access the app

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 4. Create an account

1. Go to http://localhost:3000/register
2. Create an account
3. Start tracking crypto!

## Project Structure

```
cryptoflyt/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── workers/         # Celery tasks
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API client
│   │   └── store/           # Zustand stores
│   └── package.json
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login |
| GET | /api/prices/current | Get all prices |
| WS | /api/prices/ws | Real-time price stream |
| POST | /api/prices/analyze | AI market analysis |
| GET | /api/alerts | Get user alerts |
| POST | /api/alerts | Create alert |
| GET | /api/portfolio | Get portfolio |
| POST | /api/portfolio/holdings | Add holding |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection | Auto |
| REDIS_URL | Redis connection | Auto |
| SECRET_KEY | JWT secret | Yes |
| GOOGLE_API_KEY | Gemini API key | No |
| TELEGRAM_BOT_TOKEN | Telegram bot | No |

## Portfolio Value

This project demonstrates:

1. **Real-time Systems** - WebSocket streaming, pub/sub
2. **Data Pipelines** - Background workers, message queues
3. **External APIs** - Bybit, Gemini, Telegram integration
4. **Full-stack Development** - FastAPI + React
5. **Database Design** - PostgreSQL, Redis caching
6. **Authentication** - JWT tokens, secure password hashing
7. **DevOps** - Docker, microservices architecture

## License

MIT
