# Deployment Guide

Guide for deploying the AI RAG Chatbot to production.

## Deployment Options

### Option 1: Docker Deployment (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p data/pdfs vectorstore

EXPOSE 8000

CMD ["uvicorn", "app15_book:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./vectorstore:/app/vectorstore
      - ./client_secret.json:/app/client_secret.json
      - ./token.json:/app/token.json
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Cloud Platforms

#### AWS EC2

1. Launch Ubuntu EC2 instance
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip redis-server
   ```
3. Clone repo and setup
4. Use systemd service or PM2 to keep running

#### Google Cloud Run

1. Build container:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/rag-chatbot
   ```
2. Deploy:
   ```bash
   gcloud run deploy rag-chatbot \
     --image gcr.io/PROJECT_ID/rag-chatbot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Heroku

1. Create `Procfile`:
   ```
   web: uvicorn app15_book:app --host 0.0.0.0 --port $PORT
   ```
2. Add Redis addon:
   ```bash
   heroku addons:create heroku-redis:mini
   ```
3. Deploy:
   ```bash
   git push heroku main
   ```

#### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build:
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn app15_book:app --host 0.0.0.0 --port 8080`
3. Add Redis database component
4. Set environment variables

### Option 3: VPS Deployment

Using PM2 for process management:

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
pm2 ecosystem

# Edit ecosystem.config.js
module.exports = {
  apps: [{
    name: 'rag-chatbot',
    script: 'uvicorn',
    args: 'app15_book:app --host 0.0.0.0 --port 8000',
    interpreter: 'python3',
    env: {
      REDIS_URL: 'redis://localhost:6379/0',
      GOOGLE_API_KEY: 'your_key_here'
    }
  }]
}

# Start
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Production Checklist

### Security

- [ ] Use HTTPS (setup SSL certificate)
- [ ] Enable CORS properly in FastAPI
- [ ] Store secrets in environment variables
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Implement rate limiting
- [ ] Add authentication/API keys
- [ ] Keep dependencies updated

### Performance

- [ ] Setup Redis persistence
- [ ] Configure Redis maxmemory policy
- [ ] Use production ASGI server (uvicorn with workers)
- [ ] Enable Gunicorn with uvicorn workers:
  ```bash
  gunicorn app15_book:app -w 4 -k uvicorn.workers.UvicornWorker
  ```
- [ ] Setup CDN for static files
- [ ] Monitor memory usage
- [ ] Setup health check endpoint

### Monitoring

- [ ] Setup logging (e.g., Sentry, LogRocket)
- [ ] Monitor uptime (UptimeRobot, Pingdom)
- [ ] Track errors and exceptions
- [ ] Monitor Redis memory
- [ ] Setup alerts

### Backup

- [ ] Backup Redis data regularly
- [ ] Backup vector store
- [ ] Version control all code
- [ ] Document recovery procedures

## Environment Variables for Production

```env
# Production settings
ENV=production
DEBUG=false

# API Keys (use secrets manager)
GOOGLE_API_KEY=xxx
GOOGLE_CLIENT_SECRET_FILE=/secrets/client_secret.json

# Redis (use managed service)
REDIS_URL=redis://user:pass@host:port/db

# CORS (adjust for your domain)
ALLOWED_ORIGINS=https://yourdomain.com

# Calendar
CALENDAR_TIME_ZONE=America/New_York
```

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (Nginx, AWS ELB)
- Share Redis instance across instances
- Share vector store (S3, EFS)
- Consider stateless design

### Vertical Scaling

- Increase memory for larger vector stores
- More CPU for concurrent requests
- SSD for faster vector retrieval

## Troubleshooting Production Issues

### High Memory Usage
- Check Redis memory: `redis-cli info memory`
- Reduce session TTL
- Implement memory limits

### Slow Response Times
- Profile with `cProfile`
- Check vector store size
- Optimize chunk size
- Add caching layer

### Calendar API Errors
- Check quota limits
- Implement retry logic
- Monitor API usage

## Support

For production issues, include:
- Server specs
- Error logs
- Traffic patterns
- Monitoring data

Happy deploying! 🚀
