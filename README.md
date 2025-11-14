# MindLab Health - Mental Health Therapist Matching Platform v2.1

A comprehensive FastAPI-based mental health platform that connects patients with therapists, featuring appointment scheduling, nutrition tracking, role-based access control, and administrative management tools.

## 🚀 Features

### Core Functionality
- **User Authentication & Authorization** - JWT-based authentication with role-based access control
- **Therapist-Patient Matching** - Intelligent matching system for mental health professionals
- **Appointment Management** - Complete scheduling system with Google Calendar integration
- **Nutrition Tracking** - Comprehensive nutrition and meal planning tools
- **Real-time Messaging** - Communication system between patients and providers
- **Analytics & Reporting** - Advanced analytics dashboard for administrators

### User Roles
- **Admin** - Full system access and management capabilities
- **Physician** - Medical professional with patient management access
- **Therapist** - Mental health professional with patient interaction tools
- **Health Coach** - Wellness coaching with nutrition focus
- **Patient** - Patient portal with appointment booking and health tracking

### Admin Features
- User Management with RBAC (Role-Based Access Control)
- System Analytics and Reporting
- Appointment Oversight
- Security Monitoring and Audit Logs
- Commission and Earnings Management
- System Settings and Configuration

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16
- **Authentication**: JWT with OAuth2
- **Frontend**: Vanilla JavaScript with modern ES6+
- **Containerization**: Podman/Docker
- **Calendar Integration**: Google Calendar API
- **Development**: Hot-reload development environment

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 16+ or Docker/Podman
- Node.js (for development tools, optional)

### Quick Start with Docker/Podman

1. **Clone the repository**
```bash
git clone https://github.com/your-username/mindlab-health.git
cd mindlab-health
```

2. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Main Application: http://localhost:8001
- Admin Panel: http://localhost:8001/dashboard.html

### Manual Installation

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Setup PostgreSQL Database**
```bash
# Create database
createdb mindlab_health

# Run migrations (automatically handled on startup)
python verify_database.py
```

3. **Run the application**
```bash
uvicorn 07_main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔐 Default Credentials

**Admin User:**
- Username: `admin`
- Password: `Admin123!@#`

**Database:**
- User: `mindlab_admin`
- Password: `MindLab2024!Secure`
- Database: `mindlab_health`

> ⚠️ **Security Note**: Change default credentials in production!

## 🏗️ Project Structure

```
mindlab_health/
├── frontend/                  # Frontend assets
│   ├── js/                   # JavaScript modules
│   │   ├── rbac.js          # Role-based access control
│   │   ├── role-dashboards.js # Dashboard functionality
│   │   └── demo-features.js  # Feature demonstrations
│   ├── index.html           # Main login page
│   ├── dashboard.html       # Admin dashboard
│   └── styles.css          # Application styles
├── 07_main.py              # Main FastAPI application
├── models.py               # Database models
├── auth.py                 # Authentication logic
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
└── .env.example           # Environment template
```

## 🔗 API Endpoints

### Authentication
- `POST /api/token` - Login endpoint
- `GET /api/users/me` - Get current user info

### User Management
- `GET /api/users` - List users (Admin only)
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user

### Appointments
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/{id}` - Update appointment

### Nutrition Tracking
- `GET /api/nutrition` - Get nutrition data
- `POST /api/nutrition` - Log nutrition entry
- `GET /api/ingredients` - Search ingredients

### Analytics (Admin)
- `GET /api/analytics/dashboard` - Dashboard analytics
- `GET /api/analytics/appointments` - Appointment analytics
- `GET /api/security/events` - Security audit logs

## 🛡️ Security Features

- **JWT Authentication** with secure token handling
- **Role-Based Access Control (RBAC)** with granular permissions
- **Password Security** with bcrypt hashing and strength validation
- **API Rate Limiting** and request validation
- **Audit Logging** for all admin actions
- **Security Event Monitoring** with alert system
- **CORS Protection** with configurable origins

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mindlab_health
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mindlab_health
POSTGRES_USER=mindlab_admin
POSTGRES_PASSWORD=MindLab2024!Secure

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Calendar (Optional)
GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/credentials.json
```

### Database Configuration

The application automatically creates all necessary tables on startup. For custom database setup:

```python
# Custom database initialization
python init_settings.py
python create_test_users.py
```

## 🚀 Deployment

### Production Deployment

1. **Update environment variables**
```bash
# Use production database credentials
# Set secure SECRET_KEY
# Configure proper CORS origins
```

2. **Build production container**
```bash
docker build -t mindlab-health:latest .
```

3. **Deploy with compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Health Checks

- API Health: `GET /api/health`
- Database Status: Check container logs
- Frontend Status: Access main page

## 📊 Monitoring & Analytics

### Built-in Analytics
- User activity tracking
- Appointment analytics
- System performance metrics
- Security event monitoring

### Admin Dashboard Features
- Real-time system statistics
- User management interface
- Appointment oversight
- Revenue and commission tracking
- Security audit trails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn 07_main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest tests/
```

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database container status
docker logs mindlab-postgres

# Verify database credentials in .env
```

2. **Authentication Problems**
```bash
# Reset admin password
python reset_admin_password.py
```

3. **Static Files Not Loading**
```bash
# Verify static file mounting in FastAPI
# Check container file permissions
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Mobile application (React Native)
- [ ] Advanced AI-powered therapist matching
- [ ] Telemedicine video integration
- [ ] Insurance billing integration
- [ ] Multi-language support
- [ ] Enhanced analytics and reporting

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**MindLab Health v2.1** - Transforming mental health care through technology.