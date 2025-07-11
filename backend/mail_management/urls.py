from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailViewSet, CategoryViewSet, NoteViewSet, UserActionViewSet

router = DefaultRouter()
router.register(r'emails', EmailViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'user-actions', UserActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
