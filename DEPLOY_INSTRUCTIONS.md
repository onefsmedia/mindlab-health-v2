# MindLab Health Deployment Instructions
## VPS: 72.60.62.202 | Domain: system.mindlabhealth.com

---

## Pre-Deployment Checklist

### 1. Configure DNS (Do this FIRST - before deployment)
Go to your domain registrar and add the following DNS record:

```
Type: A
Host: system (or system.mindlabhealth.com)
Value: 72.60.62.202
TTL: 3600 (or Auto)
```

**Wait 5-15 minutes for DNS propagation**

Verify DNS is working:
```bash
nslookup system.mindlabhealth.com
# Should return: 72.60.62.202
```

---

## Deployment Method 1: Automated (Recommended) 🚀

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

### Step 3: Answer Prompts
When the script asks:
- **Domain name:** `system.mindlabhealth.com`
- **Admin email:** `admin@mindlabhealth.com`
- **Database password:** Create a strong password (e.g., `MindLab2025!Secure`)
- **Admin password:** Create a strong admin password

---

## Deployment Method 2: Manual Step-by-Step

### 1. Connect to VPS
```bash
ssh root@72.60.62.202
```

### 2. Update System
```bash
apt update && apt upgrade -y
```

### 3. Install PostgreSQL
```bash
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE mindlab_health_production;
CREATE USER mindlab_user WITH PASSWORD 'MindLab2025!Secure';
GRANT ALL PRIVILEGES ON DATABASE mindlab_health_production TO mindlab_user;
\q
EOF
```

### 4. Install Dependencies
```bash
apt install python3 python3-pip python3-venv git nginx supervisor certbot python3-certbot-nginx -y
```

### 5. Clone Repository
```bash
cd /var/www
git clone https://github.com/onefsmedia/mindlab-health-v2.git
cd mindlab-health-v2
```

### 6. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 7. Create Environment Configuration
```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://mindlab_user:MindLab2025!Secure@localhost:5432/mindlab_health_production

# Security (Generate new key with: openssl rand -hex 32)
SECRET_KEY=your_generated_secret_key_here
ALLOWED_HOSTS=72.60.62.202,system.mindlabhealth.com

# CORS Configuration
CORS_ORIGINS=http://system.mindlabhealth.com,https://system.mindlabhealth.com,http://72.60.62.202

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourStrongAdminPassword123!
ADMIN_EMAIL=admin@mindlabhealth.com

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
ENVIRONMENT=production

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/var/www/mindlab-health-v2/uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mindlab-health.log

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_DIR=/var/www/mindlab-health-v2/backups
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
EOF
```

**Generate SECRET_KEY and JWT_SECRET_KEY:**
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
```

Copy the generated keys and update them in the `.env` file:
```bash
nano .env
# Replace the placeholder keys with generated ones
```

### 8. Initialize Database
```bash
source venv/bin/activate
python 07_main.py
```

Wait until you see "Application startup complete", then press `Ctrl+C`.

### 9. Configure Supervisor (Process Manager)
```bash
cat > /etc/supervisor/conf.d/mindlab-health.conf << 'EOF'
[program:mindlab-health]
command=/var/www/mindlab-health-v2/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000
directory=/var/www/mindlab-health-v2
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/mindlab-health.err.log
stdout_logfile=/var/log/mindlab-health.out.log
environment=PATH="/var/www/mindlab-health-v2/venv/bin"
stopasgroup=true
killasgroup=true
EOF

# Start the service
supervisorctl reread
supervisorctl update
supervisorctl start mindlab-health
supervisorctl status
```

### 10. Configure Nginx (Reverse Proxy)
```bash
cat > /etc/nginx/sites-available/mindlab-health << 'EOF'
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
EOF

# Enable site
ln -s /etc/nginx/sites-available/mindlab-health /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 11. Configure Firewall
```bash
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw --force enable
ufw status
```

### 12. Install SSL Certificate (Let's Encrypt)
```bash
certbot --nginx -d system.mindlabhealth.com
```

Follow the prompts:
- **Email:** `admin@mindlabhealth.com`
- **Terms:** Agree
- **Redirect HTTP to HTTPS:** Yes (option 2)

### 13. Test Auto-Renewal
```bash
certbot renew --dry-run
```

### 14. Set Up Automated Backups
```bash
# Create backup script
cat > /usr/local/bin/backup-mindlab.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/var/www/mindlab-health-v2/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump mindlab_health_production > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /var/www/mindlab-health-v2 \
    --exclude='/var/www/mindlab-health-v2/venv' \
    --exclude='/var/www/mindlab-health-v2/backups'

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
chmod +x /usr/local/bin/backup-mindlab.sh

# Add to crontab (runs daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-mindlab.sh >> /var/log/mindlab-backup.log 2>&1") | crontab -
```

---

## Post-Deployment Verification

### 1. Check Service Status
```bash
supervisorctl status mindlab-health
# Should show: RUNNING
```

### 2. View Logs
```bash
# Application logs
tail -f /var/log/mindlab-health.out.log

# Error logs
tail -f /var/log/mindlab-health.err.log

# Nginx access
tail -f /var/log/nginx/access.log
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# API documentation
curl http://localhost:8000/docs
```

### 4. Access Application
- **Main URL:** https://system.mindlabhealth.com
- **API Docs:** https://system.mindlabhealth.com/docs
- **Frontend:** https://system.mindlabhealth.com/frontend/index.html
- **Admin Login:** Use credentials from `.env` file

---

## Common Management Commands

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

# View real-time logs
tail -f /var/log/mindlab-health.out.log
```

### Update Application
```bash
cd /var/www/mindlab-health-v2
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart mindlab-health
```

### Database Management
```bash
# Access database
sudo -u postgres psql mindlab_health_production

# Create manual backup
sudo -u postgres pg_dump mindlab_health_production > backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql mindlab_health_production < backup_file.sql
```

### SSL Certificate Renewal
```bash
# Manual renewal
certbot renew

# Check certificate status
certbot certificates
```

### View System Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Service status
systemctl status nginx
systemctl status postgresql
supervisorctl status
```

---

## Troubleshooting

### Application Won't Start
```bash
# Check error logs
tail -n 100 /var/log/mindlab-health.err.log

# Check if port is in use
netstat -tulpn | grep 8000

# Restart services
supervisorctl restart mindlab-health
systemctl restart nginx
```

### Database Connection Error
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test database connection
sudo -u postgres psql mindlab_health_production

# Verify credentials in .env
cat /var/www/mindlab-health-v2/.env | grep DATABASE_URL
```

### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Renew certificate manually
certbot renew --force-renewal

# Check Nginx configuration
nginx -t
```

### DNS Not Resolving
```bash
# Check DNS propagation
nslookup system.mindlabhealth.com
dig system.mindlabhealth.com

# Clear DNS cache (on local machine)
# Windows: ipconfig /flushdns
# Linux: sudo systemd-resolve --flush-caches
```

---

## Security Best Practices

### 1. Change Default Passwords
- Update admin password in `.env` file
- Use strong, unique passwords
- Store passwords securely

### 2. SSH Security
```bash
# Disable root password login (use SSH keys)
nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
systemctl restart sshd
```

### 3. Install Fail2Ban
```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### 4. Regular Updates
```bash
# Update system weekly
apt update && apt upgrade -y

# Update application dependencies
cd /var/www/mindlab-health-v2
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
supervisorctl restart mindlab-health
```

### 5. Monitor Logs
```bash
# Set up log monitoring
tail -f /var/log/mindlab-health.err.log
tail -f /var/log/nginx/error.log
```

---

## Deployment Checklist

- [ ] DNS A record pointing to 72.60.62.202
- [ ] VPS accessible via SSH
- [ ] PostgreSQL installed and database created
- [ ] Python environment set up
- [ ] Application code cloned from GitHub
- [ ] Environment variables configured (.env)
- [ ] Database initialized with tables
- [ ] Supervisor configured and running
- [ ] Nginx configured and running
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] SSL certificate installed and working
- [ ] Application accessible at https://system.mindlabhealth.com
- [ ] Admin can login successfully
- [ ] Automated backups scheduled
- [ ] Monitoring set up

---

## Support & Documentation

- **GitHub Repository:** https://github.com/onefsmedia/mindlab-health-v2
- **API Documentation:** https://system.mindlabhealth.com/docs
- **Deployment Guide:** DEPLOYMENT_HOSTINGER.md
- **Quick Reference:** QUICK_REFERENCE.md

---

## Contact Information

- **Domain:** system.mindlabhealth.com
- **VPS IP:** 72.60.62.202
- **Admin Email:** admin@mindlabhealth.com
- **Support:** Create an issue on GitHub

---

**Last Updated:** November 14, 2025
**Version:** 2.0
**Status:** Production Ready ✅
