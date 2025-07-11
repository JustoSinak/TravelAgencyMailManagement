"""
URL configuration for travel_agency_mail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.decorators.csrf import csrf_exempt
import importlib.util

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mail_management.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('mail_management.urls')),  # Include mail_management URLs at root level for web interface
]

# Add GraphQL endpoint only if graphene_django is available
if importlib.util.find_spec('graphene_django') is not None:
    from graphene_django.views import GraphQLView
    urlpatterns.append(
        path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True)))
    )
