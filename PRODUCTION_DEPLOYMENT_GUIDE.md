# Production Deployment Guide

## Overview
This guide provides instructions for deploying the AI-Powered Todo application to a production environment. The application consists of a FastAPI backend and a Next.js frontend, with PostgreSQL as the database and AI services for enhanced functionality.

## Prerequisites

### Infrastructure Requirements
- Linux server (Ubuntu 20.04 LTS or newer recommended)
- Docker and Docker Compose installed
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)
- At least 2GB RAM and 2 CPU cores
- 10GB available disk space

### External Services
- PostgreSQL database (can be self-hosted or cloud service)
- OpenAI API key for AI features
- OpenRouter API key (alternative to OpenAI)
- SMTP service for email notifications (optional)

## Environment Configuration

### 1. Copy the environment template:
```bash
cp .env.prod.example .env
```

### 2. Update the environment variables:
- `DB_*` variables for database connection
- `JWT_SECRET_KEY` with a secure random string
- `OPENAI_API_KEY` and/or `OPENROUTER_API_KEY` for AI features
- `NEXT_PUBLIC_API_URL` for frontend API calls
- `ALLOWED_ORIGINS` with your domain

## Deployment Steps

### Option 1: Docker Compose Deployment (Recommended)

#### 1. Prepare the server:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-powered-todo.git
cd ai-powered-todo
```

#### 3. Configure environment variables:
```bash
cp .env.prod.example .env
# Edit .env with your specific values
nano .env
```

#### 4. Build and start the services:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

#### 5. Verify the deployment:
```bash
# Check if all containers are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 2: Manual Deployment

#### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install poetry
poetry install --only=main
```

#### Frontend Setup:
```bash
cd frontend
npm install
npm run build
npm start
```

## SSL Certificate Setup (Production)

### Using Let's Encrypt with Nginx:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Reverse Proxy Configuration

### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Migration

### Run database migrations:
```bash
# If using Alembic for migrations
docker-compose exec backend alembic upgrade head
```

## Security Best Practices

### 1. Firewall Configuration:
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Regular Updates:
```bash
# Update system packages regularly
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 3. Backup Strategy:
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/todo_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "todo_backup_*.sql" -mtime +7 -delete
```

## Monitoring and Logging

### 1. Application Logs:
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f

# Monitor logs with rotation
docker-compose -f docker-compose.prod.yml logs --tail=100 -f
```

### 2. System Monitoring:
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor resource usage
htop
```

## Performance Optimization

### 1. Database Optimization:
- Enable connection pooling
- Create proper indexes
- Regular vacuum and analyze

### 2. Application Caching:
- Implement Redis for session storage
- Cache frequently accessed data
- Optimize API responses

### 3. CDN Setup:
- Serve static assets through CDN
- Enable gzip compression
- Optimize images

## Troubleshooting

### Common Issues:

#### Application not starting:
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

#### Database connection errors:
```bash
# Test database connection
docker-compose exec backend pg_isready
```

#### SSL certificate issues:
```bash
# Check certificate status
sudo certbot certificates
```

## Rollback Procedure

### To rollback to a previous version:
```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Pull previous version
git reset --hard <previous-commit-hash>

# Rebuild and deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

## Maintenance Schedule

### Daily:
- Check application logs
- Verify backup completion

### Weekly:
- Update system packages
- Check disk space usage

### Monthly:
- Review security patches
- Update application dependencies
- Test disaster recovery procedures

## Contact Information

For deployment issues, contact:
- DevOps Team: devops@yourcompany.com
- Support: support@yourcompany.com