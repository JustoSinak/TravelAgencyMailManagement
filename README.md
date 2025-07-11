# Travel Agency Mail Management System

A comprehensive email management system built with Django, featuring machine learning-powered email classification, real-time notifications, and advanced user interaction capabilities.

## Features

### Part A: Backend Development with Django and API Design
- **Environment Setup**: Complete Django project with virtual environment, dependencies, and security configurations
- **Database Design**: Robust schema with Users, Emails, Categories, Notes, and UserActions models with proper indexing
- **RESTful APIs**: Comprehensive API endpoints with serializers, viewsets, and URL routing for CRUD operations
- **Authentication & Security**: JWT authentication, CSRF protection, rate limiting, and security headers

### Part B: Frontend Development (Django Templates)
- **Email Catalog**: Modern responsive interface with search, pagination, and filtering functionality
- **Real-Time Features**: WebSocket connections using Django Channels for live email updates and notifications
- **User Notes System**: Note-taking functionality with minimum 10-character validation and user attribution
- **GraphQL Integration**: Complete GraphQL schema with queries and mutations for efficient data fetching

### Part C: Machine Learning and API Integration
- **ML Service**: FastAPI-based email classification service with TF-IDF vectorization and Naive Bayes classification
- **Recommendation Engine**: Collaborative filtering system with user action tracking and similarity calculations
- **Docker Support**: Containerized ML service with Docker configuration

## Architecture

```
├── backend/                    # Django Backend
│   ├── mail_management/       # Main Django App
│   │   ├── models.py          # Database Models
│   │   ├── views.py           # API Views & Web Views
│   │   ├── serializers.py     # DRF Serializers
│   │   ├── schema.py          # GraphQL Schema
│   │   ├── consumers.py       # WebSocket Consumers
│   │   ├── tasks.py           # Celery Tasks
│   │   ├── notifications.py   # Real-time Notifications
│   │   └── templates/         # Django Templates
│   ├── travel_agency_mail/    # Django Project Settings
│   ├── requirements.txt       # Python Dependencies
│   └── Dockerfile            # Docker Configuration
├── ml_service/               # Machine Learning Service
│   ├── main.py              # FastAPI Application
│   ├── recommendation_engine.py # Recommendation System
│   ├── requirements.txt     # ML Dependencies
│   └── Dockerfile          # ML Service Docker
└── docker-compose.yml      # Multi-service Docker Setup
```

## Technology Stack

### Backend
- **Django 5.2.4**: Web framework
- **Django REST Framework**: API development
- **Django Channels**: WebSocket support
- **Celery**: Asynchronous task processing
- **PostgreSQL**: Primary database
- **Redis**: Caching and message broker
- **JWT**: Authentication

### Frontend
- **Django Templates**: Server-side rendering
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **WebSocket**: Real-time communication

### Machine Learning
- **FastAPI**: ML service framework
- **scikit-learn**: Machine learning algorithms
- **NLTK**: Natural language processing
- **TF-IDF**: Text vectorization
- **Naive Bayes**: Classification algorithm

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd travel-agency-mail-management
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/api/
- GraphQL Playground: http://localhost:8000/graphql/
- ML Service: http://localhost:8001

### Option 2: Manual Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

2. **ML Service Setup**
```bash
cd ml_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

3. **Start Celery Workers**
```bash
cd backend
celery -A travel_agency_mail worker --loglevel=info
celery -A travel_agency_mail beat --loglevel=info
```

## Key Features Demonstration

### 1. Email Management
- **Dashboard**: Overview of email statistics and recent activity
- **Email Catalog**: Searchable, filterable email list with pagination
- **Priority System**: High, Medium, Low priority classification
- **Category Management**: Automatic ML-powered categorization

### 2. Real-Time Features
- **Live Notifications**: Instant updates when emails are classified
- **WebSocket Connection**: Real-time communication between client and server
- **Status Updates**: Live email count and priority updates

### 3. Note-Taking System
- **Rich Notes**: Add, edit, and delete notes with minimum 10-character validation
- **User Attribution**: Track note authors and timestamps
- **Quick Actions**: Pre-defined note templates for common responses

### 4. Machine Learning Integration
- **Email Classification**: Automatic categorization using Naive Bayes
- **Recommendation Engine**: Collaborative filtering for email suggestions
- **Text Processing**: Advanced NLP with TF-IDF vectorization

### 5. API Capabilities
- **REST API**: Full CRUD operations for all entities
- **GraphQL**: Flexible query language for efficient data fetching
- **Authentication**: JWT-based secure API access

## Configuration

### Environment Variables
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=travel_mail_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ML Service
ML_SERVICE_URL=http://localhost:8001

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## API Documentation

### REST API Endpoints
- `GET /api/emails/` - List emails
- `POST /api/emails/` - Create email
- `GET /api/emails/{id}/` - Get email details
- `POST /api/emails/{id}/mark_as_read/` - Mark email as read
- `GET /api/emails/recommendations/` - Get recommendations
- `GET /api/categories/` - List categories
- `POST /api/notes/` - Create note
- `GET /api/user-actions/` - List user actions

### GraphQL Queries
```graphql
# Get all emails with categories and notes
query GetEmails {
  emails {
    id
    subject
    sender
    receivedAt
    priority
    isRead
    categories {
      name
    }
    notes {
      content
      author {
        username
      }
    }
  }
}

# Create a new note
mutation CreateNote($emailId: ID!, $content: String!) {
  createNote(emailId: $emailId, content: $content) {
    success
    errors
    note {
      id
      content
    }
  }
}
```

##  Testing

### Run Tests
```bash
cd backend
python manage.py test
```

### Test ML Service
```bash
cd ml_service
pytest
```

## Performance Features

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Redis-based caching for frequently accessed data
- **Pagination**: Efficient data loading with pagination
- **Asynchronous Processing**: Background tasks with Celery
- **Real-time Updates**: WebSocket connections for live data

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **CSRF Protection**: Cross-site request forgery protection
- **Rate Limiting**: API rate limiting to prevent abuse
- **Security Headers**: Comprehensive security headers
- **Input Validation**: Robust input validation and sanitization

## Deployment

The application is containerized and ready for deployment with Docker Compose. For production deployment:

1. Update environment variables for production
2. Configure SSL/TLS certificates
3. Set up proper database backups
4. Configure monitoring and logging
5. Scale services as needed

## License

This project is developed for educational purposes as part of a technical assessment.

## Contributing

This is an assessment project. For questions or clarifications, please contact the development team.

---

**Built with Django, FastAPI, and modern web technologies**
