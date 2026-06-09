# Boxing Management API - Production Deployment Guide

## Quick Start

### Local Development
```bash
docker-compose up -d
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Adminer: http://localhost:8080
```

### Environment Variables (.env)
```
POSTGRES_USER=trevor
POSTGRES_PASSWORD=supersecure
POSTGRES_DB=boxing
REDIS_HOST=redis
REDIS_PORT=6379
APP_ENV=development
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Production Deployment

### 1. AWS ECS/Fargate
```bash
# Push image
docker tag boxing-api:dhi your-account.dkr.ecr.us-east-1.amazonaws.com/boxing-api:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/boxing-api:latest

# Deploy with Terraform or CloudFormation
```

### 2. Kubernetes
```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

### 3. Docker Swarm
```bash
docker stack deploy -c docker-compose.prod.yml boxing
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Enable HTTPS/TLS with certificates
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Use secrets vault (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable rate limiting
- [ ] Configure CORS properly per environment
- [ ] Set up API keys for external integrations
- [ ] Enable audit logging
- [ ] Regular security updates

## Monitoring & Logging

### Error Tracking
- Sentry: https://sentry.io
- Set SENTRY_DSN in environment variables

### Logging
- ELK Stack: Elasticsearch + Logstash + Kibana
- CloudWatch: AWS native logging
- Datadog: All-in-one platform

### Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Database Backups

```bash
# Daily automated backups
0 2 * * * pg_dump boxing > /backups/boxing_$(date +\%Y\%m\%d).sql

# Restore from backup
psql boxing < /backups/boxing_20240101.sql
```

## CI/CD Pipeline

Push to GitHub → GitHub Actions → Tests → Build → Push to Registry → Deploy

See `.github/workflows/ci-cd.yml` for full configuration

## Scaling Strategies

1. **Horizontal**: Multiple API instances behind load balancer
2. **Vertical**: Increase container resources
3. **Database**: Read replicas for queries, writes to primary
4. **Caching**: Redis for sessions, frequently accessed data
5. **CDN**: CloudFront for static assets

## Performance Optimization

- Connection pooling: 10-20 connections
- Query optimization with indexes
- Caching with Redis
- Compression (gzip)
- CDN for static files
- Database query timeouts

## API Rate Limiting

Default: 100 requests per 60 seconds per IP

Configure in settings.py:
```python
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 60
```

## API Documentation

- Swagger UI: http://api.example.com/docs
- ReDoc: http://api.example.com/redoc
- OpenAPI Schema: http://api.example.com/openapi.json

## Support & Troubleshooting

Check logs:
```bash
docker logs api
docker logs db
docker logs redis
```

View database:
```bash
# Via Adminer: http://localhost:8080
# Via psql
psql -h db -U trevor -d boxing
```

## Next Steps

1. Set up GitHub repository
2. Configure CI/CD secrets
3. Choose deployment platform (AWS, GCP, Azure, DigitalOcean)
4. Set up monitoring (Sentry, DataDog, CloudWatch)
5. Configure backups and disaster recovery
6. Build frontend applications
7. Set up custom domain and SSL certificates
