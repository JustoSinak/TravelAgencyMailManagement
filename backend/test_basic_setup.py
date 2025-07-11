#!/usr/bin/env python
"""
Basic setup test for Travel Agency Mail Management System
This script tests if the minimal Django setup is working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_agency_mail.settings')

def test_django_setup():
    """Test if Django can be set up without errors"""
    try:
        django.setup()
        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_database_connection():
    """Test if database connection works"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models_import():
    """Test if models can be imported"""
    try:
        from mail_management.models import User, Email, Category, Note, UserAction
        print("✅ Models import successful")
        return True
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False

def test_views_import():
    """Test if views can be imported"""
    try:
        from mail_management.views import email_catalog, email_notes, dashboard
        print("✅ Views import successful")
        return True
    except Exception as e:
        print(f"❌ Views import failed: {e}")
        return False

def test_urls_import():
    """Test if URLs can be imported"""
    try:
        from travel_agency_mail.urls import urlpatterns
        print(f"✅ URLs import successful ({len(urlpatterns)} patterns)")
        return True
    except Exception as e:
        print(f"❌ URLs import failed: {e}")
        return False

def test_optional_features():
    """Test which optional features are available"""
    features = {}
    
    try:
        import channels
        features['WebSocket (Channels)'] = True
    except ImportError:
        features['WebSocket (Channels)'] = False
    
    try:
        import graphene_django
        features['GraphQL'] = True
    except ImportError:
        features['GraphQL'] = False
    
    try:
        import celery
        features['Background Tasks (Celery)'] = True
    except ImportError:
        features['Background Tasks (Celery)'] = False
    
    try:
        import sklearn
        features['Machine Learning'] = True
    except ImportError:
        features['Machine Learning'] = False
    
    print("\n📋 Optional Features Status:")
    for feature, available in features.items():
        status = "✅ Available" if available else "❌ Not installed"
        print(f"   {feature}: {status}")
    
    return features

def main():
    """Run all tests"""
    print("🧪 Testing Travel Agency Mail Management System Setup")
    print("=" * 60)
    
    tests = [
        test_django_setup,
        test_database_connection,
        test_models_import,
        test_views_import,
        test_urls_import,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Test optional features
    features = test_optional_features()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} core tests passed")
    
    if passed == total:
        print("🎉 Basic setup is working correctly!")
        print("\n🚀 You can now run:")
        print("   python manage.py migrate")
        print("   python manage.py runserver")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    # Show next steps based on available features
    print("\n📝 Next Steps:")
    if not features['WebSocket (Channels)']:
        print("   • Install channels for real-time features: pip install channels channels-redis")
    if not features['GraphQL']:
        print("   • Install GraphQL support: pip install graphene-django")
    if not features['Background Tasks (Celery)']:
        print("   • Install Celery for background tasks: pip install celery redis")
    if not features['Machine Learning']:
        print("   • Install ML features: pip install scikit-learn numpy nltk")

if __name__ == "__main__":
    main()
