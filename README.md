# Boxing Management API

A production-ready FastAPI backend for managing boxing events, fighters, matches, training sessions, and user accounts.

## Features

### ✅ Core Features
- **User Management**: Registration, login, JWT authentication
- **Fighter Profiles**: Create and manage fighter profiles with stats
- **Matches/Bouts**: Schedule, track, and record boxing matches
- **Events/Tournaments**: Organize boxing tournaments and events
- **Training Sessions**: Log and track fighter training workouts

### ✅ Production Features
- **Security**: JWT authentication, rate limiting, CORS, input validation
- **Database**: PostgreSQL with Alembic migrations, connection pooling
- **Caching**: Redis for sessions and frequently accessed data
- **Monitoring**: Sentry integration, health checks, structured logging
- **Testing**: Unit tests, integration tests, code coverage
- **CI/CD**: GitHub Actions pipeline for auto-build and deploy
- **Deployment**: Docker, Kubernetes, AWS/GCP ready

### ✅ Advanced Features (Coming Soon)
- Email notifications
- Media uploads (S3)
- Payment processing (Stripe)
- Analytics & statistics
- Search & filtering
- Webhooks
- API rate limiting per user

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.14+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/boxing-api.git
cd boxing-api

# Start services
docker-compose up -d

# Access endpoints
# API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
# Database Admin: http://localhost:8080 (Adminer)
```

### Environment Variables

Copy `.env.development` to `.env` for local testing:
```bash
cp .env.development .env
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `GET /auth/users` - List all users
- `DELETE /auth/users/{id}` - Delete user account

### Fighters
- `POST /fighters` - Create fighter profile
- `GET /fighters` - List all fighters
- `GET /fighters/{id}` - Get fighter details
- `PUT /fighters/{id}` - Update fighter profile
- `DELETE /fighters/{id}` - Delete fighter

### Matches
- `POST /matches` - Create match
- `GET /matches` - List matches
- `GET /matches/{id}` - Get match details
- `PUT /matches/{id}` - Update match result
- `DELETE /matches/{id}` - Delete match

### Events
- `POST /events` - Create event
- `GET /events` - List events
- `GET /events/{id}` - Get event details
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event

### Training
- `POST /training` - Log training session
- `GET /training` - List your training sessions
- `GET /training/{id}` - Get session details
- `DELETE /training/{id}` - Delete session

## API Authentication

Add JWT token to request headers:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/me
```

Get token by logging in:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## Deployment

### Docker Hub
```bash
docker build -t yourusername/boxing-api:latest .
docker push yourusername/boxing-api:latest
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yml
kubectl get pods -n boxing
```

### Production with Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Architecture

```
┌─────────────────────────────────────────┐
│         Client Applications             │
│  (Web UI, Mobile, Third-party APIs)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     FastAPI Application (DHI Python)    │
│  - Rate Limiting Middleware             │
│  - JWT Authentication                   │
│  - Request Validation                   │
│  - Error Handling                       │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐
│ PgSQL  │ │Redis │ │Prometheus
│Database│ │Cache │ │Monitoring
└────────┘ └──────┘ └────────┘
```

## Performance Optimization

- **Connection Pooling**: 10-20 database connections
- **Query Optimization**: Indexed frequently-queried fields
- **Caching**: Redis for sessions and hot data
- **Compression**: gzip enabled
- **CDN**: Ready for CloudFront/Cloudflare
- **Rate Limiting**: 100 requests per 60 seconds

## Security

- JWT tokens with 30-minute expiration
- Bcrypt password hashing
- SQL injection protection via SQLAlchemy ORM
- CORS configuration per environment
- Rate limiting per IP address
- Input validation with Pydantic
- Secrets in environment variables (never in code)

## Monitoring & Logging

- **Sentry**: Real-time error tracking
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health Checks**: `/health` endpoint
- **Structured Logging**: JSON-formatted logs

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Create Pull Request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/boxing-api/issues
- Email: support@boxingapi.com
- Documentation: https://docs.boxingapi.com

## Roadmap

- [ ] Email notifications
- [ ] S3 media uploads
- [ ] Stripe payment processing
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Webhooks for external integrations
- [ ] GraphQL API
- [ ] WebSocket real-time updates
