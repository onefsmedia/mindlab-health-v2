# Deploy to Hostinger VPS (72.60.62.202)

## Quick Start - Automated Deployment

### Step 1: Connect to VPS
```bash
ssh root@72.60.62.202
```

### Step 2: Run Automated Deployment
```bash
# Download deployment script
wget https://raw.githubusercontent.com/onefsmedia/mindlab-health-v2/master/deploy_hostinger.sh

# Make executable
chmod +x deploy_hostinger.sh

# Run deployment
./deploy_hostinger.sh
```

The script will ask you for:
- Domain name (e.g., yourdomain.com)
- Admin email for SSL certificate
- Database password
- Admin password for the application

---

## Manual Deployment (Step-by-Step)

### Step 1: Connect to VPS
```bash
ssh root@72.60.62.202
```

### Step 2: Update System
```bash
apt update && apt upgrade -y
```

### Step 3: Install PostgreSQL
```bash
# Install PostgreSQL
apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE mindlab_health_production;
CREATE USER mindlab_user WITH PASSWORD 'ChangeThisPassword123!';
GRANT ALL PRIVILEGES ON DATABASE mindlab_health_production TO mindlab_user;
\q
EOF
```

### Step 4: Install Python and Dependencies
```bash
apt install python3 python3-pip python3-venv git nginx supervisor certbot python3-certbot-nginx -y
```

### Step 5: Clone Repository
```bash
cd /var/www
git clone https://github.com/onefsmedia/mindlab-health-v2.git
cd mindlab-health-v2
```

### Step 6: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 7: Configure Environment Variables
```bash
nano .env
```

**Update these values:**
```env
# Database Configuration
DATABASE_URL=postgresql://mindlab_user:ChangeThisPassword123!@localhost:5432/mindlab_health_production

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=72.60.62.202,system.mindlabhealth.com

# CORS (Update with your domain)
CORS_ORIGINS=http://system.mindlabhealth.com,https://system.mindlabhealth.com,http://72.60.62.202

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourStrongPassword123!
ADMIN_EMAIL=admin@mindlabhealth.com

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
ENVIRONMENT=production
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 8: Initialize Database
```bash
source venv/bin/activate
python 07_main.py
```

This will:
- Create all database tables
- Create admin user
- Initialize the system

**Press `Ctrl+C` after you see "Application startup complete"**

### Step 9: Set Up Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn (optional)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000
# Press Ctrl+C to stop after testing
```

### Step 10: Configure Supervisor
```bash
nano /etc/supervisor/conf.d/mindlab-health.conf
```

**Add this configuration:**
```ini
[program:mindlab-health]
command=/var/www/mindlab-health-v2/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000
directory=/var/www/mindlab-health-v2
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/mindlab-health.err.log
stdout_logfile=/var/log/mindlab-health.out.log
environment=PATH="/var/www/mindlab-health-v2/venv/bin"
```

**Start the service:**
```bash
supervisorctl reread
supervisorctl update
supervisorctl start mindlab-health
supervisorctl status
```

### Step 11: Configure Nginx
```bash
nano /etc/nginx/sites-available/mindlab-health
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name system.mindlabhealth.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /var/www/mindlab-health-v2/static;
        expires 30d;
    }

    location /frontend {
        alias /var/www/mindlab-health-v2/frontend;
        try_files $uri $uri/ =404;
    }
}
```

**Enable the site:**
```bash
ln -s /etc/nginx/sites-available/mindlab-health /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 12: Configure Firewall
```bash
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw --force enable
ufw status
```

### Step 13: Test Your Deployment
```bash
# Check if service is running
supervisorctl status mindlab-health

# Check logs
tail -f /var/log/mindlab-health.out.log
```

**Access your application:**
- HTTP: http://system.mindlabhealth.com (or http://72.60.62.202 before DNS)
- API Docs: http://system.mindlabhealth.com/docs
- Frontend: http://system.mindlabhealth.com/frontend/index.html

---

## Optional: Set Up Domain and SSL

### Set Up Domain and SSL

**Step 1: Point DNS to VPS**
Before proceeding, make sure your domain DNS is configured:
- Go to your domain registrar (e.g., Namecheap, GoDaddy)
- Add an A record: `system.mindlabhealth.com` → `72.60.62.202`
- Wait 5-15 minutes for DNS propagation

**Step 2: Update Nginx Config**
```bash
nano /etc/nginx/sites-available/mindlab-health
```

Change:
```nginx
server_name 72.60.62.202;
```

To:
```nginx
server_name system.mindlabhealth.com;
```

**Step 3: Restart Nginx**
```bash
nginx -t
systemctl restart nginx
```

**Step 4: Install SSL Certificate**
```bash
certbot --nginx -d system.mindlabhealth.com
```

Follow the prompts:
- Enter your email
- Accept Terms of Service
- Choose to redirect HTTP to HTTPS (option 2)

**Step 3: Test Auto-Renewal**
```bash
certbot renew --dry-run
```

---

## Common Commands

### Service Management
```bash
# Check status
supervisorctl status mindlab-health

# Restart application
supervisorctl restart mindlab-health

# Stop application
supervisorctl stop mindlab-health

# Start application
supervisorctl start mindlab-health
```

### View Logs
```bash
# Application logs
tail -f /var/log/mindlab-health.out.log

# Error logs
tail -f /var/log/mindlab-health.err.log

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Update Application
```bash
cd /var/www/mindlab-health-v2
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart mindlab-health
```

### Database Backup
```bash
# Create backup
sudo -u postgres pg_dump mindlab_health_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
sudo -u postgres psql mindlab_health_production < backup_file.sql
```

### Check System Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# PostgreSQL status
systemctl status postgresql

# Nginx status
systemctl status nginx
```

---

## Troubleshooting

### Application won't start
```bash
# Check logs
tail -n 50 /var/log/mindlab-health.err.log

# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Restart everything
supervisorctl restart mindlab-health
systemctl restart nginx
```

### Database connection error
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test database connection
sudo -u postgres psql mindlab_health_production

# Check .env file has correct credentials
cat /var/www/mindlab-health-v2/.env | grep DATABASE_URL
```

### Nginx errors
```bash
# Test Nginx configuration
nginx -t

# View error logs
tail -f /var/log/nginx/error.log

# Restart Nginx
systemctl restart nginx
```

### Permission errors
```bash
# Fix ownership
chown -R root:root /var/www/mindlab-health-v2

# Fix permissions
chmod -R 755 /var/www/mindlab-health-v2
```

---

## Post-Deployment Checklist

- [ ] Application accessible at http://72.60.62.202
- [ ] API documentation at http://72.60.62.202/docs
- [ ] Can login with admin credentials
- [ ] Database connection working
- [ ] Supervisor keeping app running
- [ ] Nginx reverse proxy working
- [ ] Logs being written correctly
- [ ] Firewall configured
- [ ] SSL certificate installed (if using domain)
- [ ] Auto-renewal for SSL configured
- [ ] Backup script scheduled

---

## Security Recommendations

1. **Change default passwords** in .env file
2. **Use strong SECRET_KEY** (32+ characters)
3. **Keep system updated**: `apt update && apt upgrade`
4. **Monitor logs regularly**
5. **Set up automated backups**
6. **Use SSH keys** instead of password authentication
7. **Configure fail2ban** for brute-force protection
8. **Keep PostgreSQL updated**

---

## Support

For detailed documentation, see:
- DEPLOYMENT_HOSTINGER.md - Full deployment guide
- QUICK_REFERENCE.md - Command reference
- README.md - Application overview

GitHub Repository: https://github.com/onefsmedia/mindlab-health-v2
