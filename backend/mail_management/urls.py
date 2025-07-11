from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailViewSet, CategoryViewSet, NoteViewSet, UserActionViewSet, email_catalog, email_notes, dashboard, edit_note, delete_note, graphql_playground, web_login, web_register, web_logout
from .authentication import register, login, logout, user_profile, update_profile

router = DefaultRouter()
router.register(r'emails', EmailViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'user-actions', UserActionViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/logout/', logout, name='logout'),
    path('api/auth/profile/', user_profile, name='user_profile'),
    path('api/auth/profile/update/', update_profile, name='update_profile'),

    # Authentication endpoints
    path('auth/login/', web_login, name='web_login'),
    path('auth/register/', web_register, name='web_register'),
    path('auth/logout/', web_logout, name='web_logout'),

    # Web interface endpoints
    path('', dashboard, name='home'),  # Root URL goes to dashboard
    path('dashboard/', dashboard, name='dashboard'),
    path('emails/catalog/', email_catalog, name='email_catalog'),
    path('emails/<int:email_id>/notes/', email_notes, name='email_notes'),
    path('notes/<int:note_id>/edit/', edit_note, name='edit_note'),
    path('notes/<int:note_id>/delete/', delete_note, name='delete_note'),
    path('graphql-playground/', graphql_playground, name='graphql_playground'),
]
