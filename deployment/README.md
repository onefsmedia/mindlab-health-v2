# MindLab Health - Deployment Guide

## 🐳 Podman Desktop Deployment

This guide covers deploying MindLab Health using Podman Desktop.

## Prerequisites

1. **Podman Desktop** - Download from [podman-desktop.io](https://podman-desktop.io/)
2. **Python 3.11+** - For running deployment scripts
3. **Git** - For cloning the repository

## Quick Start

### 1. Install Podman Desktop

Download and install Podman Desktop for your operating system:
- Windows: Use the installer from podman-desktop.io
- macOS: Use Homebrew or installer
- Linux: Use package manager

### 2. Start Podman Machine (Windows/Mac only)

```bash
podman machine init
podman machine start
```

### 3. Configure Environment

```bash
cd mindlab_health_v2/deployment
cp .env.example .env
# Edit .env and update passwords and secrets
```

### 4. Deploy Application

#### Option A: Automated Deployment (Recommended)

```bash
python deploy.py
```

This script will:
- ✅ Check Podman installation
- ✅ Build container images
- ✅ Start all services
- ✅ Wait for health checks
- ✅ Display status and access points

#### Option B: Manual Deployment

```bash
# Build images
podman compose build

# Start services
podman compose up -d

# Check status
podman compose ps
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Nginx (Port 80/443)                │
│          Reverse Proxy + SSL/TLS                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         FastAPI Application (Port 8000)         │
│    • REST API endpoints                         │
│    • JWT authentication                         │
│    • Frontend serving                           │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│       PostgreSQL Database (Port 5432)           │
│    • User data                                  │
│    • Appointments                               │
│    • Messages                                   │
│    • Persistent volume                          │
└─────────────────────────────────────────────────┘
```

## Access Points

After deployment:

- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Database**: postgresql://postgres:password@localhost:5432/mindlab_health

## Management Commands

### View Logs

```bash
# Application logs
podman logs -f mindlab_app

# Database logs
podman logs -f mindlab_postgres

# All services
podman compose logs -f
```

### Stop Services

```bash
podman compose down
```

### Restart Services

```bash
podman compose restart
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
podman compose build
podman compose up -d
```

### Database Backup

```bash
# Backup database
podman exec mindlab_postgres pg_dump -U postgres mindlab_health > backup.sql

# Restore database
cat backup.sql | podman exec -i mindlab_postgres psql -U postgres mindlab_health
```

## Production Deployment

### 1. Update Environment Variables

Edit `.env` file:

```bash
# Strong passwords
POSTGRES_PASSWORD=your-strong-password-here
SECRET_KEY=your-jwt-secret-key-here

# Production settings
ENVIRONMENT=production
DEBUG=false
```

### 2. Configure SSL/TLS

Place SSL certificates in `deployment/ssl/`:

```
deployment/ssl/
├── certificate.crt
└── private.key
```

Update `nginx.conf` to enable HTTPS.

### 3. Enable Nginx (Production Profile)

```bash
podman compose --profile production up -d
```

### 4. Security Checklist

- [ ] Update all passwords in `.env`
- [ ] Generate new JWT secret key
- [ ] Configure SSL certificates
- [ ] Enable firewall rules
- [ ] Set up monitoring and logging
- [ ] Configure backup schedule
- [ ] Review and update CORS settings
- [ ] Enable rate limiting

## Troubleshooting

### Container won't start

```bash
# Check container logs
podman logs mindlab_app

# Check container status
podman ps -a

# Inspect container
podman inspect mindlab_app
```

### Database connection issues

```bash
# Check if database is running
podman exec mindlab_postgres pg_isready -U postgres

# Check database logs
podman logs mindlab_postgres

# Connect to database
podman exec -it mindlab_postgres psql -U postgres mindlab_health
```

### Port already in use

```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Stop existing containers
podman stop mindlab_app mindlab_postgres
podman rm mindlab_app mindlab_postgres
```

### Reset everything

```bash
# Stop and remove all containers
podman compose down -v

# Remove images
podman rmi mindlab_health_v2-app

# Remove volumes (WARNING: deletes all data)
podman volume rm mindlab_health_v2_postgres_data

# Start fresh
python deploy.py
```

## Monitoring

### Container Stats

```bash
podman stats
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/health

# Database health
podman exec mindlab_postgres pg_isready -U postgres
```

## Scaling (Future)

For scaling beyond a single machine:

1. **Kubernetes/OpenShift**: Migrate to container orchestration
2. **Load Balancing**: Add multiple app instances
3. **Database Replication**: Set up PostgreSQL replicas
4. **Caching**: Add Redis for session management
5. **CDN**: Serve static assets from CDN

## Support

For issues or questions:

1. Check logs: `podman logs -f mindlab_app`
2. Review documentation: `http://localhost:8000/docs`
3. Check Podman Desktop dashboard
4. Verify environment variables in `.env`

## License

MindLab Health - Healthcare appointment and messaging platform
