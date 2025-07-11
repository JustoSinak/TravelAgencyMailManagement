#!/bin/bash

# Travel Agency Mail Management System Setup Script
echo "🚀 Setting up Travel Agency Mail Management System..."

# Check if running on Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server
    
    # Create python symlink if it doesn't exist
    if ! command -v python &> /dev/null; then
        sudo apt-get install -y python-is-python3
    fi
fi

# Function to setup backend
setup_backend() {
    echo "🔧 Setting up Django Backend..."
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies with increased timeout and retries
    echo "📥 Installing Python dependencies (this may take a while)..."
    pip install --timeout 60 --retries 5 -r requirements.txt
    
    # Alternative installation if the above fails
    if [ $? -ne 0 ]; then
        echo "⚠️  Standard installation failed, trying alternative approach..."
        
        # Install core dependencies first
        pip install Django==5.2.4
        pip install djangorestframework==3.15.2
        pip install django-cors-headers==4.3.1
        pip install python-dotenv==1.0.0
        pip install djangorestframework-simplejwt==5.3.0
        pip install psycopg2-binary==2.9.7
        
        # Install channels without redis initially
        pip install channels==4.0.0
        
        # Try to install channels-redis separately
        pip install --timeout 120 channels-redis==4.2.0 || pip install channels-redis==4.1.0 || echo "⚠️  channels-redis installation failed, WebSocket features may not work"
        
        # Install remaining packages
        pip install graphene-django==3.2.0 || echo "⚠️  GraphQL features may not work"
        pip install celery==5.3.4
        pip install django-celery-beat==2.5.0 || echo "⚠️  Celery beat may not work"
        pip install django-celery-results==2.5.1 || echo "⚠️  Celery results may not work"
        pip install redis==5.0.1
        pip install requests==2.31.0
        pip install scikit-learn==1.3.2 || echo "⚠️  ML features may not work"
        pip install joblib==1.3.2
        pip install numpy==1.24.4
        pip install pytest==7.4.3
        pip install pytest-django==4.7.0
        pip install factory-boy==3.3.0
        pip install drf-spectacular==0.27.0
        pip install Pillow==10.1.0
    fi
    
    echo "✅ Backend dependencies installed"
    cd ..
}

# Function to setup ML service
setup_ml_service() {
    echo "🤖 Setting up ML Service..."
    cd ml_service
    
    # Create virtual environment for ML service
    python3 -m venv ml_venv
    source ml_venv/bin/activate
    
    # Install ML dependencies
    pip install --upgrade pip
    pip install --timeout 60 --retries 5 -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Standard ML installation failed, trying alternative approach..."
        pip install fastapi==0.104.1
        pip install "uvicorn[standard]==0.24.0"
        pip install pydantic==2.5.0
        pip install scikit-learn==1.3.2 || echo "⚠️  scikit-learn installation failed"
        pip install joblib==1.3.2
        pip install numpy==1.24.4
        pip install pandas==2.1.4
        pip install nltk==3.8.1 || echo "⚠️  NLTK installation failed"
        pip install python-multipart==0.0.6
        pip install httpx==0.25.2
    fi
    
    echo "✅ ML Service dependencies installed"
    cd ..
}

# Function to setup database
setup_database() {
    echo "🗄️  Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE travel_mail_db;" 2>/dev/null || echo "Database already exists"
    sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'password';" 2>/dev/null || echo "User already exists"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE travel_mail_db TO postgres;" 2>/dev/null
    
    echo "✅ Database setup complete"
}

# Function to setup Redis
setup_redis() {
    echo "🔴 Setting up Redis..."
    
    # Start Redis service
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    echo "✅ Redis setup complete"
}

# Function to run Django migrations
run_migrations() {
    echo "🔄 Running Django migrations..."
    cd backend
    source venv/bin/activate
    
    python manage.py migrate
    
    echo "👤 Creating superuser (optional)..."
    echo "You can create a superuser account now or skip this step."
    read -p "Create superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py createsuperuser
    fi
    
    cd ..
    echo "✅ Migrations complete"
}

# Main setup process
main() {
    echo "🎯 Starting setup process..."
    
    # Check if Docker is available
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo "🐳 Docker detected! You can use Docker Compose for easier setup."
        echo "Run: docker-compose up -d"
        echo ""
        read -p "Use Docker setup instead? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose up -d
            echo "✅ Docker setup complete!"
            echo "🌐 Access the application at: http://localhost:8000"
            exit 0
        fi
    fi
    
    # Manual setup
    setup_backend
    setup_ml_service
    setup_database
    setup_redis
    run_migrations
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Start the Django backend:"
    echo "   cd backend && source venv/bin/activate && python manage.py runserver"
    echo ""
    echo "2. Start the ML service (in another terminal):"
    echo "   cd ml_service && source ml_venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8001"
    echo ""
    echo "3. Start Celery worker (in another terminal):"
    echo "   cd backend && source venv/bin/activate && celery -A travel_agency_mail worker --loglevel=info"
    echo ""
    echo "4. Access the application:"
    echo "   🌐 Web Interface: http://localhost:8000"
    echo "   📚 API Docs: http://localhost:8000/api/"
    echo "   🔍 GraphQL: http://localhost:8000/graphql/"
    echo "   🤖 ML Service: http://localhost:8001"
    echo ""
}

# Run main function
main "$@"
