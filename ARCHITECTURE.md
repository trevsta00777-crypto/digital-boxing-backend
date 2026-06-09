# Architecture & System Design

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer (LB)                     │
│              (Nginx, HAProxy, AWS ALB, etc)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
   │ API Pod  │      │ API Pod  │      │ API Pod  │
   │ Instance │      │ Instance │      │ Instance │
   │    1     │      │    2     │      │    N     │
   └────┬─────┘      └────┬─────┘      └────┬─────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼──────┐      ┌────▼──────┐    ┌────▼──────┐
   │ Primary   │      │  Read     │    │   Cache   │
   │ Database  │      │  Replicas │    │   (Redis) │
   │(PostgreSQL│      │           │    │           │
   │ Primary)  │      │(Read-only)│    │           │
   └───────────┘      └───────────┘    └───────────┘
        │
   ┌────▼──────┐
   │  Backups  │
   │(S3/Cloud) │
   └───────────┘
```

## Components

### API Layer (FastAPI)
- **Framework**: FastAPI with Uvicorn workers
- **Instances**: 3-10 replicas (auto-scaling)
- **Security**: JWT auth, rate limiting, CORS
- **Validation**: Pydantic models, input sanitization

### Database Layer (PostgreSQL)
- **Primary**: Write operations
- **Replicas**: Read-only, load distributed
- **Connection Pool**: 10-20 connections
- **Migrations**: Alembic for versioning
- **Backups**: Automated daily snapshots

### Cache Layer (Redis)
- **Sessions**: JWT token caching
- **Hot Data**: Frequently accessed fighters/matches
- **Rate Limiting**: Token bucket algorithm
- **Pub/Sub**: Real-time notifications (future)

### Monitoring
- **Errors**: Sentry real-time alerts
- **Metrics**: Prometheus scraping
- **Visualization**: Grafana dashboards
- **Logs**: Centralized ELK or CloudWatch

## Data Models

### Entity Relationships
```
User (1) ─── (N) Fighter
         │
         └─── (N) TrainingSession

Fighter (1) ─── (N) Match
Event (1) ─── (N) Match
Match involves 2 Fighters
```

### Database Schema
```sql
Users
├── id (PK)
├── email (UNIQUE)
├── username (UNIQUE)
├── hashed_password
├── full_name
├── is_active
├── created_at
└── updated_at

Fighters
├── id (PK)
├── user_id (FK)
├── name
├── nickname
├── weight_class
├── height
├── reach
├── wins
├── losses
├── draws
├── bio
├── created_at
└── updated_at

Matches
├── id (PK)
├── event_id (FK, nullable)
├── fighter1_id (FK)
├── fighter2_id (FK)
├── rounds
├── duration_minutes
├── status
├── winner_id (FK)
├── fighter1_score
├── fighter2_score
├── result
├── notes
├── match_date
├── created_at
└── updated_at

Events
├── id (PK)
├── name
├── description
├── location
├── event_date
├── status
├── created_at
└── updated_at

TrainingSessions
├── id (PK)
├── user_id (FK)
├── fighter_id (FK, nullable)
├── session_type
├── duration_minutes
├── exercises
├── intensity
├── notes
├── calories_burned
├── session_date
├── created_at
└── updated_at
```

## Request Flow

```
1. Client Request
   │
   ├─ Load Balancer routes to API instance
   │
   ├─ API receives request
   │
   ├─ Rate Limiter checks limit
   │
   ├─ JWT middleware validates token
   │
   ├─ Route handler processes request
   │
   ├─ Query Redis cache
   │ └─ Cache miss → Query PostgreSQL
   │ └─ Store result in Redis
   │
   ├─ Format response
   │
   └─ Return to client
```

## Scaling Strategy

### Horizontal Scaling
1. **API Layer**: Auto-scale based on CPU (70%) & Memory (80%)
2. **Range**: Minimum 3, Maximum 10 instances
3. **Load Balancer**: Distributes traffic round-robin

### Vertical Scaling
1. **Increase container resources**
2. **Add more database connections**
3. **Increase Redis memory**

### Database Scaling
1. **Read Replicas**: 2-3 for read-heavy operations
2. **Sharding**: If database exceeds capacity
3. **Connection Pooling**: PgBouncer for connection management

### Caching Strategy
1. **Session Data**: 30 minutes TTL
2. **Fighter Stats**: 1 hour TTL
3. **Event Data**: 4 hours TTL
4. **Cache Invalidation**: Event-based updates

## Deployment Environments

### Development
- Local Docker Compose
- Single instance all services
- Debug logging enabled
- Rate limits relaxed (1000 req/min)

### Staging
- AWS ECS/Fargate or Kubernetes
- 2 API instances
- Production database copy
- Rate limits: 100 req/min

### Production
- AWS ECS/Fargate or Kubernetes
- 3+ API instances (auto-scaling)
- Managed RDS PostgreSQL
- Managed Redis (ElastiCache)
- CloudFront CDN
- Route 53 DNS

## Security Layers

1. **Network**: TLS/HTTPS, firewall rules, VPC
2. **Authentication**: JWT tokens, password hashing (bcrypt)
3. **Authorization**: Role-based access control (RBAC)
4. **Validation**: Input sanitization, type checking
5. **Database**: Parameterized queries, encryption at rest
6. **Secrets**: AWS Secrets Manager, HashiCorp Vault
7. **Monitoring**: Audit logs, anomaly detection

## Performance Targets

- **API Response Time**: < 200ms (p99)
- **Database Query Time**: < 100ms (p99)
- **Cache Hit Rate**: > 80%
- **Availability**: 99.9% uptime
- **Throughput**: 1000+ requests/second

## Disaster Recovery

- **RPO** (Recovery Point Objective): 1 hour
- **RTO** (Recovery Time Objective): 15 minutes
- **Backup Strategy**: Daily snapshots → S3/Cloud Storage
- **Multi-Region**: Active-Passive setup (future)
