#!/bin/bash

# MindLab Health - Quick Deployment Script for Hostinger VPS
# ===========================================================
# This script automates the deployment process on Ubuntu

set -e  # Exit on error

echo "======================================"
echo "MindLab Health - Hostinger Deployment"
echo "======================================"
echo ""

# Configuration
APP_DIR="/var/www/mindlab-health"
APP_NAME="mindlab-health"
PYTHON_VERSION="3.10"
DB_NAME="mindlab_health_production"
DB_USER="mindlab_user"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing required packages...${NC}"
apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip
apt-get install -y build-essential libpq-dev postgresql postgresql-contrib
apt-get install -y nginx supervisor git curl wget

echo -e "${GREEN}Step 3: Creating application user and directories...${NC}"
if ! id -u mindlab >/dev/null 2>&1; then
    adduser --system --group --home ${APP_DIR} mindlab
fi

mkdir -p ${APP_DIR}/app
mkdir -p /var/log/${APP_NAME}
mkdir -p /var/backups/${APP_NAME}
mkdir -p ${APP_DIR}/uploads

chown -R mindlab:mindlab ${APP_DIR}
chown -R mindlab:mindlab /var/log/${APP_NAME}
chown -R mindlab:mindlab /var/backups/${APP_NAME}

echo -e "${GREEN}Step 4: Setting up PostgreSQL...${NC}"
systemctl start postgresql
systemctl enable postgresql

# Prompt for database password
echo -e "${YELLOW}Enter a secure password for database user '${DB_USER}':${NC}"
read -s DB_PASSWORD
echo ""

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
sudo -u postgres psql -c "ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};"

echo -e "${GREEN}Step 5: Cloning repository...${NC}"
if [ ! -d "${APP_DIR}/app/.git" ]; then
    echo -e "${YELLOW}Enter GitHub repository URL:${NC}"
    read REPO_URL
    sudo -u mindlab git clone ${REPO_URL} ${APP_DIR}/app
else
    echo "Repository already cloned, pulling latest changes..."
    cd ${APP_DIR}/app
    sudo -u mindlab git pull
fi

echo -e "${GREEN}Step 6: Setting up Python virtual environment...${NC}"
cd ${APP_DIR}/app
sudo -u mindlab python${PYTHON_VERSION} -m venv venv
sudo -u mindlab ${APP_DIR}/app/venv/bin/pip install --upgrade pip setuptools wheel
sudo -u mindlab ${APP_DIR}/app/venv/bin/pip install -r requirements.txt

echo -e "${GREEN}Step 7: Configuring environment variables...${NC}"
if [ ! -f "${APP_DIR}/app/.env" ]; then
    cp ${APP_DIR}/app/.env.example ${APP_DIR}/app/.env
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Update .env file
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}|" ${APP_DIR}/app/.env
    sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|" ${APP_DIR}/app/.env
    sed -i "s|DEBUG=.*|DEBUG=False|" ${APP_DIR}/app/.env
    
    chown mindlab:mindlab ${APP_DIR}/app/.env
    chmod 600 ${APP_DIR}/app/.env
    
    echo -e "${YELLOW}Please edit ${APP_DIR}/app/.env to set your domain and other settings${NC}"
else
    echo ".env file already exists, skipping..."
fi

echo -e "${GREEN}Step 8: Creating Gunicorn configuration...${NC}"
cat > ${APP_DIR}/app/gunicorn_config.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
accesslog = "/var/log/mindlab-health/access.log"
errorlog = "/var/log/mindlab-health/error.log"
loglevel = "info"
proc_name = "mindlab_health"
user = "mindlab"
group = "mindlab"
EOF

chown mindlab:mindlab ${APP_DIR}/app/gunicorn_config.py

echo -e "${GREEN}Step 9: Configuring Supervisor...${NC}"
cat > /etc/supervisor/conf.d/${APP_NAME}.conf << EOF
[program:${APP_NAME}]
directory=${APP_DIR}/app
command=${APP_DIR}/app/venv/bin/gunicorn -c ${APP_DIR}/app/gunicorn_config.py 07_main:app
user=mindlab
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/${APP_NAME}/supervisor_error.log
stdout_logfile=/var/log/${APP_NAME}/supervisor_access.log
environment=PATH="${APP_DIR}/app/venv/bin"
EOF

supervisorctl reread
supervisorctl update

echo -e "${GREEN}Step 10: Configuring Nginx...${NC}"
echo -e "${YELLOW}Enter your domain name (e.g., example.com):${NC}"
read DOMAIN_NAME

cat > /etc/nginx/sites-available/${APP_NAME} << EOF
upstream mindlab_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};
    
    client_max_body_size 10M;
    
    access_log /var/log/nginx/${APP_NAME}-access.log;
    error_log /var/log/nginx/${APP_NAME}-error.log;
    
    location /static/ {
        alias ${APP_DIR}/app/static/;
        expires 30d;
    }
    
    location /frontend/ {
        alias ${APP_DIR}/app/frontend/;
        try_files \$uri \$uri/ /frontend/index.html;
    }
    
    location / {
        proxy_pass http://mindlab_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo -e "${GREEN}Step 11: Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo -e "${GREEN}Step 12: Starting application...${NC}"
supervisorctl start ${APP_NAME}
sleep 3
supervisorctl status ${APP_NAME}

echo -e "${GREEN}Step 13: Creating backup script...${NC}"
cat > ${APP_DIR}/app/backup_database.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/${APP_NAME}"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/backup_\$DATE.sql"
pg_dump -U ${DB_USER} -h localhost ${DB_NAME} > "\$BACKUP_FILE"
gzip "\$BACKUP_FILE"
find "\$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x ${APP_DIR}/app/backup_database.sh
chown mindlab:mindlab ${APP_DIR}/app/backup_database.sh

# Add to crontab
(crontab -u mindlab -l 2>/dev/null; echo "0 2 * * * ${APP_DIR}/app/backup_database.sh >> /var/log/${APP_NAME}/backup.log 2>&1") | crontab -u mindlab -

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit ${APP_DIR}/app/.env and update:"
echo "   - CORS_ORIGINS (add your domain)"
echo "   - DEFAULT_ADMIN_PASSWORD"
echo "   - Other settings as needed"
echo ""
echo "2. Install SSL certificate:"
echo "   sudo apt-get install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d ${DOMAIN_NAME} -d www.${DOMAIN_NAME}"
echo ""
echo "3. Restart the application:"
echo "   sudo supervisorctl restart ${APP_NAME}"
echo ""
echo "4. Access your application:"
echo "   http://${DOMAIN_NAME}"
echo ""
echo "5. Check logs if needed:"
echo "   sudo tail -f /var/log/${APP_NAME}/error.log"
echo ""
echo -e "${GREEN}Database Credentials:${NC}"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
echo "Password: [saved in .env file]"
echo ""
echo -e "${YELLOW}IMPORTANT: Save these credentials securely!${NC}"
echo ""
