from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailViewSet, CategoryViewSet, NoteViewSet, UserActionViewSet, email_catalog, email_notes

router = DefaultRouter()
router.register(r'emails', EmailViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'user-actions', UserActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('emails/catalog/', email_catalog, name='email_catalog'),
    path('emails/<int:email_id>/notes/', email_notes, name='email_notes'),
]
