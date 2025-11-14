# MindLab Health - Hostinger VPS Deployment Guide
# ================================================
# Ubuntu Server Deployment with Python/FastAPI

## Prerequisites

- Hostinger VPS with Ubuntu 20.04 or 22.04
- Root or sudo access
- Domain name pointed to VPS IP
- SSH access configured

## Quick Start Deployment

### 1. System Preparation

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y python3.10 python3.10-venv python3-pip
sudo apt-get install -y build-essential libpq-dev postgresql postgresql-contrib
sudo apt-get install -y nginx supervisor git curl

# Install PostgreSQL 14+ (recommended)
sudo apt-get install -y postgresql-14 postgresql-client-14
```

### 2. Create Application User

```bash
# Create dedicated user for the application
sudo adduser --system --group --home /var/www/mindlab-health mindlab

# Create necessary directories
sudo mkdir -p /var/www/mindlab-health
sudo mkdir -p /var/log/mindlab-health
sudo mkdir -p /var/backups/mindlab-health
sudo mkdir -p /var/www/mindlab-health/uploads

# Set ownership
sudo chown -R mindlab:mindlab /var/www/mindlab-health
sudo chown -R mindlab:mindlab /var/log/mindlab-health
sudo chown -R mindlab:mindlab /var/backups/mindlab-health
```

### 3. Clone Repository

```bash
# Switch to mindlab user
sudo su - mindlab

# Clone your repository
cd /var/www/mindlab-health
git clone https://github.com/onefsmedia/mindlab-health-v2.git app

# Or upload files via SCP/SFTP
cd app
```

### 4. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Run these commands in PostgreSQL prompt:
CREATE DATABASE mindlab_health_production;
CREATE USER mindlab_user WITH PASSWORD 'YOUR_SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE mindlab_health_production TO mindlab_user;
ALTER DATABASE mindlab_health_production OWNER TO mindlab_user;

# Grant schema privileges
\c mindlab_health_production
GRANT ALL ON SCHEMA public TO mindlab_user;

# Exit PostgreSQL
\q
```

### 6. Configure Environment Variables

```bash
# Copy and edit .env file
cd /var/www/mindlab-health/app
cp .env.example .env
nano .env

# Update these critical values:
# - DATABASE_URL (use the password you set above)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - DEFAULT_ADMIN_PASSWORD
# - CORS_ORIGINS (add your domain)
```

### 7. Initialize Database

```bash
# Activate virtual environment
source /var/www/mindlab-health/app/venv/bin/activate

# Run the application once to create tables
cd /var/www/mindlab-health/app
python 07_main.py

# Or use Alembic migrations (if configured)
# alembic upgrade head
```

### 8. Configure Gunicorn

Create `/var/www/mindlab-health/app/gunicorn_config.py`:

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/mindlab-health/access.log"
errorlog = "/var/log/mindlab-health/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "mindlab_health"

# Server mechanics
daemon = False
pidfile = "/var/run/mindlab-health.pid"
umask = 0
user = "mindlab"
group = "mindlab"
```

### 9. Configure Supervisor

Create `/etc/supervisor/conf.d/mindlab-health.conf`:

```ini
[program:mindlab-health]
directory=/var/www/mindlab-health/app
command=/var/www/mindlab-health/app/venv/bin/gunicorn -c /var/www/mindlab-health/app/gunicorn_config.py 07_main:app
user=mindlab
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/mindlab-health/supervisor_error.log
stdout_logfile=/var/log/mindlab-health/supervisor_access.log
environment=PATH="/var/www/mindlab-health/app/venv/bin"
```

Apply configuration:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mindlab-health
sudo supervisorctl status
```

### 10. Configure Nginx

Create `/etc/nginx/sites-available/mindlab-health`:

```nginx
upstream mindlab_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/mindlab-health-access.log;
    error_log /var/log/nginx/mindlab-health-error.log;

    # Static files
    location /static/ {
        alias /var/www/mindlab-health/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend
    location /frontend/ {
        alias /var/www/mindlab-health/app/frontend/;
        try_files $uri $uri/ /frontend/index.html;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://mindlab_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Root location
    location / {
        proxy_pass http://mindlab_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/mindlab-health /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

### 12. Set Up Automated Backups

Create `/var/www/mindlab-health/app/backup_database.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/mindlab-health"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mindlab_backup_$DATE.sql"
RETENTION_DAYS=30

# Create backup
pg_dump -U mindlab_user -h localhost mindlab_health_production > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Delete old backups
find "$BACKUP_DIR" -name "mindlab_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

Make executable and add to crontab:

```bash
chmod +x /var/www/mindlab-health/app/backup_database.sh

# Add to crontab (run daily at 2 AM)
sudo crontab -e -u mindlab
# Add this line:
0 2 * * * /var/www/mindlab-health/app/backup_database.sh >> /var/log/mindlab-health/backup.log 2>&1
```

### 13. Firewall Configuration

```bash
# Install and configure UFW
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## Monitoring & Maintenance

### Check Application Status

```bash
# Check supervisor status
sudo supervisorctl status mindlab-health

# View logs
sudo tail -f /var/log/mindlab-health/error.log
sudo tail -f /var/log/nginx/mindlab-health-error.log

# Restart application
sudo supervisorctl restart mindlab-health
```

### Update Application

```bash
# Switch to mindlab user
sudo su - mindlab
cd /var/www/mindlab-health/app

# Pull latest changes
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations (if any)
# alembic upgrade head

# Exit mindlab user
exit

# Restart application
sudo supervisorctl restart mindlab-health
```

### Database Backup/Restore

```bash
# Manual backup
sudo -u mindlab pg_dump -U mindlab_user mindlab_health_production > backup.sql

# Restore from backup
sudo -u mindlab psql -U mindlab_user mindlab_health_production < backup.sql
```

## Security Checklist

- [ ] Changed default admin password
- [ ] Generated secure JWT_SECRET_KEY
- [ ] Updated DATABASE_URL with strong password
- [ ] Configured SSL/HTTPS with Let's Encrypt
- [ ] Set up firewall (UFW)
- [ ] Disabled PostgreSQL remote access (unless needed)
- [ ] Set proper file permissions (644 for files, 755 for directories)
- [ ] Configured automated backups
- [ ] Set up monitoring/alerting (optional)
- [ ] Removed .env from git tracking
- [ ] Enabled rate limiting
- [ ] Configured CORS with specific domains

## Performance Optimization

1. **Gunicorn Workers**: Adjust based on CPU cores (2 × cores + 1)
2. **PostgreSQL**: Tune postgresql.conf for your VPS RAM
3. **Nginx Caching**: Enable for static assets
4. **Redis**: Add Redis for session caching (optional)
5. **CDN**: Use Cloudflare for static assets (optional)

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo tail -100 /var/log/mindlab-health/error.log
sudo supervisorctl tail -f mindlab-health stderr
```

### Database connection errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U mindlab_user -h localhost -d mindlab_health_production
```

### 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo supervisorctl status mindlab-health

# Check Nginx configuration
sudo nginx -t
```

## Support

For issues or questions:
- Check logs: `/var/log/mindlab-health/`
- GitHub: https://github.com/onefsmedia/mindlab-health-v2
- Email: admin@yourdomain.com
