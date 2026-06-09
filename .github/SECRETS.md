# GitHub Actions - Required Secrets

To set up CI/CD, add these secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add each secret below

## Required Secrets

### Docker Registry
```
DOCKER_USERNAME = your-dockerhub-username
DOCKER_PASSWORD = your-dockerhub-password
```

### AWS (for ECS/ECR deployment)
```
AWS_ACCESS_KEY_ID = your-aws-access-key
AWS_SECRET_ACCESS_KEY = your-aws-secret-key
AWS_REGION = us-east-1
```

### Deployment
```
DEPLOY_KEY = your-ssh-private-key-for-server
DEPLOY_HOST = your-production-server.com
DEPLOY_USER = deploy-user
```

### Database
```
DB_HOST = your-db-host.com
DB_USER = prod_user
DB_PASSWORD = your-secure-password
```

### Monitoring
```
SENTRY_DSN = https://your-key@sentry.io/project-id
```

## Setting Secrets via CLI

```bash
gh secret set DOCKER_USERNAME --body "your-username"
gh secret set DOCKER_PASSWORD --body "your-password"
```

## Using Secrets in Workflows

Reference in `.github/workflows/ci-cd.yml`:
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```
