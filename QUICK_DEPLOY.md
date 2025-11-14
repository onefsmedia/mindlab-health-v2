# Quick Manual Deployment for system.mindlabhealth.com
# Run these commands on your VPS (ssh root@72.60.62.202)

## Step 1: Install Required Packages
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3 (uses whatever version is available)
apt install -y python3 python3-pip python3-venv python3-dev

# Install database and tools
apt install -y postgresql postgresql-contrib build-essential libpq-dev

# Install web server and process manager
apt install -y nginx supervisor

# Install SSL certificate tool
apt install -y certbot python3-certbot-nginx git

# Verify Python version
python3 --version
```

## Step 2: Set Up PostgreSQL Database
```bash
# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user (run as one command)
sudo -u postgres psql << 'EOSQL'
CREATE DATABASE mindlab_health_production;
CREATE USER mindlab_user WITH PASSWORD 'MindLab2025!SecureDB';
GRANT ALL PRIVILEGES ON DATABASE mindlab_health_production TO mindlab_user;
ALTER DATABASE mindlab_health_production OWNER TO mindlab_user;
\c mindlab_health_production
GRANT ALL ON SCHEMA public TO mindlab_user;
GRANT CREATE ON SCHEMA public TO mindlab_user;
EOSQL

# Test connection
sudo -u postgres psql -d mindlab_health_production -c "SELECT version();"
```

## Step 3: Clone Application
```bash
# Create directory and clone
cd /var/www
git clone https://github.com/onefsmedia/mindlab-health-v2.git
cd mindlab-health-v2

# Verify files
ls -la
```

## Step 4: Set Up Python Environment
```bash
# Create virtual environment (uses system python3)
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install production server
pip install gunicorn

# Verify installations
pip list | grep -E "fastapi|uvicorn|gunicorn"
```

## Step 5: Create Environment Configuration
```bash
# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://mindlab_user:MindLab2025!SecureDB@localhost:5432/mindlab_health_production

# Security (run: openssl rand -hex 32)
SECRET_KEY=REPLACE_WITH_GENERATED_KEY
JWT_SECRET_KEY=REPLACE_WITH_GENERATED_KEY

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
ENVIRONMENT=production

# Hosts
ALLOWED_HOSTS=72.60.62.202,system.mindlabhealth.com
CORS_ORIGINS=http://system.mindlabhealth.com,https://system.mindlabhealth.com

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=AdminPass123!
ADMIN_EMAIL=admin@mindlabhealth.com

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Files
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/var/www/mindlab-health-v2/uploads
LOG_FILE=/var/log/mindlab-health.log
EOF

# Generate secret keys
echo ""
echo "Copy these keys to your .env file:"
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo ""

# Edit .env and paste the keys
nano .env
```

## Step 6: Initialize Database
```bash
# Make sure venv is active
cd /var/www/mindlab-health-v2
source venv/bin/activate

# Run application to create tables
python 07_main.py

# Wait for "Application startup complete" then press Ctrl+C
```

## Step 7: Configure Supervisor
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

# Start service
supervisorctl reread
supervisorctl update
supervisorctl start mindlab-health

# Check status
supervisorctl status
```

## Step 8: Configure Nginx
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
rm -f /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
```

## Step 9: Configure Firewall
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

## Step 10: Install SSL Certificate
```bash
# Make sure DNS is pointing to your VPS first!
# nslookup system.mindlabhealth.com should return 72.60.62.202

certbot --nginx -d system.mindlabhealth.com

# Follow prompts:
# Email: admin@mindlabhealth.com
# Agree to Terms: Y
# Redirect HTTP to HTTPS: 2
```

## Step 11: Verify Deployment
```bash
# Check service
supervisorctl status mindlab-health

# Check logs
tail -f /var/log/mindlab-health.out.log

# Test endpoint
curl http://localhost:8000/api/health

# Test through domain
curl https://system.mindlabhealth.com/api/health
```

## Access Your Application
- **URL:** https://system.mindlabhealth.com
- **API Docs:** https://system.mindlabhealth.com/docs
- **Frontend:** https://system.mindlabhealth.com/frontend/index.html
- **Login:** admin / AdminPass123! (change this!)

## Useful Commands
```bash
# Restart app
supervisorctl restart mindlab-health

# View logs
tail -f /var/log/mindlab-health.out.log

# Update app
cd /var/www/mindlab-health-v2
git pull
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart mindlab-health
```

## Troubleshooting
```bash
# If app won't start
tail -n 100 /var/log/mindlab-health.err.log

# Test manually
cd /var/www/mindlab-health-v2
source venv/bin/activate
gunicorn -w 1 -k uvicorn.workers.UvicornWorker 07_main:app --bind 0.0.0.0:8000

# Check PostgreSQL
systemctl status postgresql
sudo -u postgres psql mindlab_health_production
```
