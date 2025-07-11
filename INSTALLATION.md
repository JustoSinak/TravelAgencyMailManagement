# Installation Guide - Travel Agency Mail Management System

## 🚨 **Quick Fix for Current Issues**

### **Issue 1: Python Command Not Found**
```bash
# Install python-is-python3 to create python symlink
sudo apt update
sudo apt install python-is-python3

# Or use python3 directly
python3 --version
```

### **Issue 2: Network Timeout Issues**
If you're experiencing network timeouts, try these solutions:

#### **Option A: Use the Setup Script (Recommended)**
```bash
# Make the script executable and run it
chmod +x setup.sh
./setup.sh
```

#### **Option B: Manual Installation with Minimal Dependencies**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install minimal requirements first
pip install --timeout 120 --retries 3 -r requirements-minimal.txt

# Test basic functionality
python manage.py migrate
python manage.py runserver
```

#### **Option C: Install Optional Features Separately**
After the minimal installation works:
```bash
# Install real-time features (optional)
pip install --timeout 120 channels==4.0.0
pip install --timeout 120 channels-redis==4.2.0

# Install GraphQL (optional)
pip install --timeout 120 graphene-django==3.2.0

# Install task queue (optional)
pip install --timeout 120 celery==5.3.4 redis==5.0.1

# Install ML features (optional)
pip install --timeout 120 scikit-learn==1.3.2 numpy==1.24.4
```

## 🐳 **Docker Alternative (Easiest)**

If you have Docker installed, this is the simplest approach:

```bash
# Start all services with Docker
docker-compose up -d

# Access the application
# Web: http://localhost:8000
# ML Service: http://localhost:8001
```

## 🔧 **Manual Setup (Step by Step)**

### **1. System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server

# Create python symlink
sudo apt install python-is-python3
```

### **2. Database Setup**
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres createdb travel_mail_db
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"
```

### **3. Redis Setup**
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### **4. Backend Setup**
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install minimal dependencies
pip install --upgrade pip
pip install --timeout 120 -r requirements-minimal.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### **5. ML Service Setup (Optional)**
```bash
cd ml_service

# Create virtual environment
python3 -m venv ml_venv
source ml_venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install --timeout 120 -r requirements.txt

# Start ML service
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🚀 **Testing the Installation**

### **Basic Functionality Test**
```bash
# Test Django backend
curl http://localhost:8000/api/

# Test ML service (if installed)
curl http://localhost:8001/health
```

### **Web Interface Test**
1. Open browser: http://localhost:8000
2. You should see the mail management interface
3. Try creating a user account and logging in

## 🔍 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Package Installation Timeouts**
```bash
# Increase timeout and use different index
pip install --timeout 300 --index-url https://pypi.org/simple/ package-name

# Or use conda instead
conda install package-name
```

#### **2. PostgreSQL Connection Issues**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d travel_mail_db
```

#### **3. Redis Connection Issues**
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

#### **4. Port Already in Use**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

## 🎯 **Minimal Working Setup**

If you just want to see the basic functionality:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install Django==5.2.4 djangorestframework==3.15.2 python-dotenv==1.0.0
python manage.py migrate
python manage.py runserver
```

This will give you:
- ✅ Basic Django backend
- ✅ REST API endpoints
- ✅ Web interface
- ❌ Real-time features (requires channels-redis)
- ❌ ML classification (requires scikit-learn)
- ❌ Background tasks (requires celery)

## 📞 **Getting Help**

If you continue to have issues:

1. **Check the logs**: Look for specific error messages
2. **Try Docker**: Often easier than manual installation
3. **Use minimal setup**: Start with basic functionality first
4. **Check network**: Some packages may require VPN or different network

## 🎉 **Success Indicators**

You'll know the installation is successful when:

- ✅ Django server starts without errors
- ✅ You can access http://localhost:8000
- ✅ Database migrations complete successfully
- ✅ You can create and view emails in the interface

---

**Need more help?** Check the main README.md for detailed feature documentation.
