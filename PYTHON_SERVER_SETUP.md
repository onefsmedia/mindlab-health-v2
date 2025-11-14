# MindLab Health - VPS Python Server Setup Guide
## Deploy FastAPI Application with Gunicorn on Ubuntu VPS

---

## Overview

This guide will help you set up a **Python FastAPI server** on your Hostinger VPS using:
- **FastAPI** - Python web framework
- **Gunicorn** - Python WSGI HTTP Server (production-grade)
- **Uvicorn Workers** - ASGI server for async support
- **Nginx** - Reverse proxy
- **PostgreSQL** - Database
- **Supervisor** - Process management
- **SSL/TLS** - HTTPS encryption

**Domain:** system.mindlabhealth.com  
**VPS IP:** 72.60.62.202

---

## Prerequisites

### 1. DNS Configuration (Do FIRST)
Add this A record in your domain DNS:
```
Type: A
Host: system
Value: 72.60.62.202
TTL: 3600
```

Wait 5-15 minutes, then verify:
```bash
nslookup system.mindlabhealth.com
# Should return: 72.60.62.202
```

### 2. SSH Access
```bash
ssh root@72.60.62.202
```

---

## Part 1: System Setup & Python Installation

### Step 1: Update System
```bash
apt update && apt upgrade -y
```

### Step 2: Install Python 3 (Auto-detects Available Version)
```bash
# Install Python 3 and essential tools
apt install python3 python3-pip python3-venv python3-dev -y

# Verify Python installation
python3 --version
# Output: Python 3.x.x (whatever version is available)

# Verify pip installation
pip3 --version
```

**Note:** The system will use whatever Python 3.x version is available (3.9, 3.10, 3.11, etc.). Our application works with any Python 3.9+.

### Step 3: Install Build Tools & Dependencies
```bash
# PostgreSQL development files
apt install build-essential libpq-dev -y

# PostgreSQL database server
apt install postgresql postgresql-contrib -y

# Web server
apt install nginx -y

# Process manager
apt install supervisor -y

# SSL certificate manager
apt install certbot python3-certbot-nginx -y

# Version control
apt install git curl wget -y
```

---

## Part 2: PostgreSQL Database Setup

### Step 1: Start PostgreSQL
```bash
systemctl start postgresql
systemctl enable postgresql
systemctl status postgresql
```

### Step 2: Create Database and User
```bash
# Switch to postgres user and create database
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE mindlab_health_production;

-- Create user with password
CREATE USER mindlab_user WITH PASSWORD 'ChangeThisToStrongPassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mindlab_health_production TO mindlab_user;

-- Grant schema privileges (required for PostgreSQL 15+)
\c mindlab_health_production
GRANT ALL ON SCHEMA public TO mindlab_user;
GRANT CREATE ON SCHEMA public TO mindlab_user;

-- Exit
\q
EOF
```

### Step 3: Test Database Connection
```bash
# Test connection
sudo -u postgres psql -d mindlab_health_production -c "SELECT version();"
```

---

## Part 3: Application Setup (Python FastAPI Server)

### Step 1: Clone Repository
```bash
# Create application directory
cd /var/www

# Clone from GitHub
git clone https://github.com/onefsmedia/mindlab-health-v2.git

# Navigate to app directory
cd mindlab-health-v2

# Verify files are present
ls -la
# Should see: 07_main.py, models.py, requirements.txt, etc.
```

### Step 2: Create Python Virtual Environment
```bash
# Create virtual environment using system Python 3
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify you're in the virtual environment
which python
# Should show: /var/www/mindlab-health-v2/venv/bin/python

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies
```bash
# Make sure you're in virtual environment (you should see (venv) in prompt)
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt

# Install production server (Gunicorn)
pip install gunicorn

# Verify installations
pip list | grep -E "fastapi|uvicorn|gunicorn|sqlalchemy|psycopg2"
```

### Step 4: Configure Environment Variables
```bash
# Create .env file
nano .env
```

**Paste this configuration (update passwords):**
```env
# ====================================
# MindLab Health - Production Config
# ====================================

# Database Configuration
DATABASE_URL=postgresql://mindlab_user:ChangeThisToStrongPassword123!@localhost:5432/mindlab_health_production

# Security Keys (GENERATE NEW ONES - see below)
SECRET_KEY=generate_new_key_here
JWT_SECRET_KEY=generate_new_jwt_key_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
ENVIRONMENT=production

# Allowed Hosts & CORS
ALLOWED_HOSTS=72.60.62.202,system.mindlabhealth.com
CORS_ORIGINS=http://system.mindlabhealth.com,https://system.mindlabhealth.com,http://72.60.62.202

# Admin Account
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourStrongAdminPassword123!
ADMIN_EMAIL=admin@mindlabhealth.com

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/var/www/mindlab-health-v2/uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mindlab-health.log

# Database Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_DIR=/var/backups/mindlab-health
BACKUP_RETENTION_DAYS=30

# Session Configuration
SESSION_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

**Generate Security Keys:**
```bash
# Generate SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)"

# Generate JWT_SECRET_KEY
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
```

**Copy the generated keys and update them in .env:**
```bash
nano .env
# Replace the placeholder keys with generated ones
# Press Ctrl+X, then Y, then Enter to save
```

### Step 5: Initialize Database
```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run the application to create database tables
python 07_main.py
```

**Wait until you see:**
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Then press Ctrl+C to stop.**

This process:
- Creates all database tables
- Creates the admin user
- Initializes the system

---

## Part 4: Configure Gunicorn (Production Python Server)

### What is Gunicorn?
Gunicorn is a production-grade Python WSGI HTTP server that:
- Handles multiple concurrent requests
- Manages worker processes
- Provides better performance than development server
- Integrates with Uvicorn for async support (required for FastAPI)

### Step 1: Test Gunicorn
```bash
# Activate virtual environment
cd /var/www/mindlab-health-v2
source venv/bin/activate

# Test Gunicorn with Uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000
```

**Explanation of parameters:**
- `-w 4` = 4 worker processes (adjust based on CPU cores: 2-4 × CPU cores)
- `-k uvicorn.workers.UvicornWorker` = Use Uvicorn worker class for async support
- `07_main:app` = Module:variable (07_main.py contains `app` variable)
- `--bind 0.0.0.0:8000` = Listen on all interfaces, port 8000

**You should see:**
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: uvicorn.workers.UvicornWorker
```

**Press Ctrl+C to stop** (we'll set up Supervisor to manage it).

### Step 2: Configure Supervisor (Process Manager)

Supervisor ensures your Python server:
- Starts automatically on boot
- Restarts if it crashes
- Runs in the background
- Manages logs

```bash
# Create Supervisor configuration
nano /etc/supervisor/conf.d/mindlab-health.conf
```

**Paste this configuration:**
```ini
[program:mindlab-health]
# Command to run (Gunicorn with Uvicorn workers)
command=/var/www/mindlab-health-v2/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000 --timeout 120 --graceful-timeout 30

# Working directory
directory=/var/www/mindlab-health-v2

# User to run as
user=root

# Start automatically when system boots
autostart=true

# Restart automatically if it crashes
autorestart=true

# How to stop the process
stopasgroup=true
killasgroup=true

# Log files
stderr_logfile=/var/log/mindlab-health.err.log
stdout_logfile=/var/log/mindlab-health.out.log
stderr_logfile_maxbytes=10MB
stdout_logfile_maxbytes=10MB

# Environment variables
environment=PATH="/var/www/mindlab-health-v2/venv/bin"

# Priority
priority=999
```

**Save and exit:** Ctrl+X, Y, Enter

### Step 3: Start the Service
```bash
# Reload Supervisor configuration
supervisorctl reread

# Update Supervisor with new configuration
supervisorctl update

# Start the application
supervisorctl start mindlab-health

# Check status
supervisorctl status
```

**You should see:**
```
mindlab-health    RUNNING   pid 12345, uptime 0:00:05
```

### Step 4: View Logs
```bash
# View application output
tail -f /var/log/mindlab-health.out.log

# View errors (in another terminal)
tail -f /var/log/mindlab-health.err.log
```

---

## Part 5: Configure Nginx (Reverse Proxy)

### Why Nginx?
Nginx acts as a reverse proxy to:
- Handle SSL/TLS encryption
- Serve static files efficiently
- Load balance requests
- Add security headers
- Manage domain routing

### Step 1: Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/mindlab-health
```

**Paste this configuration:**
```nginx
# MindLab Health - Nginx Configuration
# Domain: system.mindlabhealth.com

server {
    listen 80;
    server_name system.mindlabhealth.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 10M;

    # Proxy to Gunicorn/FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
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

    # Static files
    location /static {
        alias /var/www/mindlab-health-v2/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend files
    location /frontend {
        alias /var/www/mindlab-health-v2/frontend;
        try_files $uri $uri/ =404;
    }

    # Uploaded files
    location /uploads {
        alias /var/www/mindlab-health-v2/uploads;
        internal;  # Only accessible through application
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }
}
```

**Save and exit:** Ctrl+X, Y, Enter

### Step 2: Enable Site
```bash
# Create symbolic link to enable site
ln -s /etc/nginx/sites-available/mindlab-health /etc/nginx/sites-enabled/

# Remove default site (optional)
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
```

**You should see:**
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Restart Nginx
```bash
systemctl restart nginx
systemctl status nginx
```

---

## Part 6: Configure Firewall

```bash
# Allow SSH (port 22)
ufw allow 22/tcp

# Allow HTTP (port 80)
ufw allow 80/tcp

# Allow HTTPS (port 443)
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## Part 7: Install SSL Certificate (HTTPS)

```bash
# Install SSL certificate for your domain
certbot --nginx -d system.mindlabhealth.com
```

**Follow the prompts:**
1. Enter email: `admin@mindlabhealth.com`
2. Agree to Terms of Service: `Y`
3. Redirect HTTP to HTTPS: `2` (Yes)

**Certbot will:**
- Obtain SSL certificate from Let's Encrypt
- Update Nginx configuration
- Enable automatic renewal

### Test Auto-Renewal
```bash
certbot renew --dry-run
```

---

## Part 8: Verify Deployment

### 1. Check Python Server (Gunicorn)
```bash
# Check if running
supervisorctl status mindlab-health
# Should show: RUNNING

# View logs
tail -f /var/log/mindlab-health.out.log
```

### 2. Check Nginx
```bash
systemctl status nginx
# Should show: active (running)
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}

# Through Nginx
curl http://system.mindlabhealth.com/api/health
curl https://system.mindlabhealth.com/api/health
```

### 4. Access Application
Open in browser:
- **Main Site:** https://system.mindlabhealth.com
- **API Docs:** https://system.mindlabhealth.com/docs
- **Frontend:** https://system.mindlabhealth.com/frontend/index.html

**Login:**
- Username: `admin`
- Password: (from .env ADMIN_PASSWORD)

---

## Management Commands

### Python Server Control (Supervisor)
```bash
# Check status
supervisorctl status mindlab-health

# Start server
supervisorctl start mindlab-health

# Stop server
supervisorctl stop mindlab-health

# Restart server
supervisorctl restart mindlab-health

# View logs
tail -f /var/log/mindlab-health.out.log
tail -f /var/log/mindlab-health.err.log
```

### Update Application
```bash
# Navigate to app directory
cd /var/www/mindlab-health-v2

# Pull latest code
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart server
supervisorctl restart mindlab-health
```

### Database Backup
```bash
# Create backup
sudo -u postgres pg_dump mindlab_health_production > /var/backups/mindlab-health/backup_$(date +%Y%m%d_%H%M%S).sql

# List backups
ls -lh /var/backups/mindlab-health/
```

### View System Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Active connections
netstat -tulpn | grep -E '8000|80|443'
```

---

## Troubleshooting

### Python Server Won't Start
```bash
# Check error logs
tail -n 100 /var/log/mindlab-health.err.log

# Test manually
cd /var/www/mindlab-health-v2
source venv/bin/activate
gunicorn -w 1 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000

# Check port
netstat -tulpn | grep 8000
```

### Database Connection Error
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test connection
sudo -u postgres psql mindlab_health_production

# Check credentials in .env
cat /var/www/mindlab-health-v2/.env | grep DATABASE_URL
```

### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Renew manually
certbot renew --force-renewal
```

---

## Performance Tuning

### Optimize Gunicorn Workers
```bash
# Calculate optimal workers: (2 × CPU_cores) + 1
nproc  # Shows number of CPU cores

# Update worker count in Supervisor config
nano /etc/supervisor/conf.d/mindlab-health.conf
# Change: -w 4 to -w X (based on your CPU)

# Restart
supervisorctl restart mindlab-health
```

### Monitor Performance
```bash
# Real-time monitoring
htop

# Check Gunicorn processes
ps aux | grep gunicorn

# Monitor logs
tail -f /var/log/mindlab-health.out.log
```

---

## Summary

You now have a **production-grade Python FastAPI server** running on your VPS:

✅ **Python Server:** Gunicorn with Uvicorn workers  
✅ **Application:** FastAPI (07_main.py)  
✅ **Database:** PostgreSQL  
✅ **Process Manager:** Supervisor (auto-restart)  
✅ **Web Server:** Nginx (reverse proxy)  
✅ **SSL:** Let's Encrypt (HTTPS)  
✅ **Domain:** system.mindlabhealth.com  
✅ **Auto-start:** Enabled on boot  

**Access:** https://system.mindlabhealth.com

---

**Need help?** Check the logs:
```bash
tail -f /var/log/mindlab-health.out.log
```
