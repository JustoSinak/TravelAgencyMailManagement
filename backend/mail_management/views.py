from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Email, Category, Note, UserAction
from .serializers import EmailSerializer, CategorySerializer, NoteSerializer, UserActionSerializer
# Import tasks only if available
try:
    from .tasks import classify_and_sort_email, record_user_action_for_recommendations, add_email_features_for_recommendations, get_user_recommendations
except ImportError:
    # Create dummy functions if tasks are not available
    def classify_and_sort_email(*args, **kwargs):
        pass
    def record_user_action_for_recommendations(*args, **kwargs):
        pass
    def add_email_features_for_recommendations(*args, **kwargs):
        pass
    def get_user_recommendations(*args, **kwargs):
        return None

class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'is_read', 'categories']
    search_fields = ['subject', 'body', 'sender']
    ordering_fields = ['received_at', 'priority', 'subject']
    ordering = ['-received_at']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        email = serializer.save(user=self.request.user)
        # Trigger ML classification asynchronously
        classify_and_sort_email.delay(email.id)
        # Add email features for recommendations
        add_email_features_for_recommendations.delay(email.id)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        email = self.get_object()
        email.mark_as_read()
        # Record user action
        UserAction.objects.create(
            user=request.user,
            email=email,
            action_type='OPEN'
        )
        # Record action for recommendations
        record_user_action_for_recommendations.delay(
            request.user.id, email.id, 'OPEN'
        )
        return Response({'status': 'email marked as read'})

    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread_emails = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_emails, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            emails = self.get_queryset().filter(categories__id=category_id)
            serializer = self.get_serializer(emails, many=True)
            return Response(serializer.data)
        return Response({'error': 'category_id parameter required'}, status=400)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get email recommendations for the current user"""
        num_recommendations = int(request.query_params.get('num_recommendations', 5))

        # Get recommendations asynchronously
        result = get_user_recommendations.delay(request.user.id, num_recommendations)

        try:
            # Wait for result (with timeout)
            recommendations = result.get(timeout=10)
            if recommendations:
                return Response(recommendations)
            else:
                return Response({'recommendations': [], 'message': 'No recommendations available'})
        except Exception as e:
            return Response({'error': 'Failed to get recommendations'}, status=500)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(email__user=self.request.user)

    def perform_create(self, serializer):
        # Validate minimum length
        content = serializer.validated_data.get('content', '')
        if len(content.strip()) < 10:
            return Response(
                {'error': 'Note content must be at least 10 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def by_email(self, request):
        email_id = request.query_params.get('email_id')
        if email_id:
            notes = self.get_queryset().filter(email_id=email_id)
            serializer = self.get_serializer(notes, many=True)
            return Response(serializer.data)
        return Response({'error': 'email_id parameter required'}, status=400)

class UserActionViewSet(viewsets.ModelViewSet):
    queryset = UserAction.objects.all()
    serializer_class = UserActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

@login_required
def email_catalog(request):
    search_term = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')
    is_read_filter = request.GET.get('is_read', '')

    emails = Email.objects.filter(user=request.user)

    # Apply filters
    if search_term:
        emails = emails.filter(
            Q(subject__icontains=search_term) |
            Q(body__icontains=search_term) |
            Q(sender__icontains=search_term)
        )

    if priority_filter:
        emails = emails.filter(priority=priority_filter)

    if is_read_filter:
        is_read = is_read_filter.lower() == 'true'
        emails = emails.filter(is_read=is_read)

    emails = emails.order_by('-received_at')

    # Pagination
    paginator = Paginator(emails, 10)  # Show 10 emails per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_emails = Email.objects.filter(user=request.user).count()
    unread_count = Email.objects.filter(user=request.user, is_read=False).count()

    context = {
        'emails': page_obj,
        'search_term': search_term,
        'priority_filter': priority_filter,
        'is_read_filter': is_read_filter,
        'total_emails': total_emails,
        'unread_count': unread_count,
    }
    return render(request, 'mail_management/email_catalog.html', context)

@login_required
def email_notes(request, email_id):
    email = get_object_or_404(Email, id=email_id, user=request.user)

    # Mark email as read when viewing
    if not email.is_read:
        email.mark_as_read()
        # Record user action for recommendations
        record_user_action_for_recommendations.delay(
            request.user.id, email.id, 'OPEN'
        )

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and len(content) >= 10:
            Note.objects.create(email=email, author=request.user, content=content)
            messages.success(request, 'Note added successfully!')
            # Record user action
            record_user_action_for_recommendations.delay(
                request.user.id, email.id, 'NOTE_ADDED', {'note_length': len(content)}
            )
            return redirect('email_notes', email_id=email.id)
        else:
            messages.error(request, 'Note content must be at least 10 characters long.')

    notes = email.notes.all().order_by('-created_at')

    context = {
        'email': email,
        'notes': notes,
    }
    return render(request, 'mail_management/email_notes.html', context)

@login_required
def dashboard(request):
    """Dashboard with email statistics and recent activity"""
    user = request.user

    # Email statistics
    total_emails = Email.objects.filter(user=user).count()
    unread_emails = Email.objects.filter(user=user, is_read=False).count()
    high_priority = Email.objects.filter(user=user, priority='H').count()

    # Recent emails
    recent_emails = Email.objects.filter(user=user).order_by('-received_at')[:5]

    # Category distribution
    from django.db.models import Count
    category_stats = Category.objects.filter(
        emails__user=user
    ).annotate(
        email_count=Count('emails')
    ).order_by('-email_count')[:5]

    # Recent notes
    recent_notes = Note.objects.filter(
        email__user=user
    ).order_by('-created_at')[:5]

    context = {
        'total_emails': total_emails,
        'unread_emails': unread_emails,
        'high_priority': high_priority,
        'recent_emails': recent_emails,
        'category_stats': category_stats,
        'recent_notes': recent_notes,
    }

    return render(request, 'mail_management/dashboard.html', context)

@login_required
def edit_note(request, note_id):
    """Edit a note"""
    note = get_object_or_404(Note, id=note_id, author=request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and len(content) >= 10:
            note.content = content
            note.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('email_notes', email_id=note.email.id)
        else:
            messages.error(request, 'Note content must be at least 10 characters long.')

    context = {
        'note': note,
        'email': note.email,
    }
    return render(request, 'mail_management/edit_note.html', context)

@login_required
def delete_note(request, note_id):
    """Delete a note"""
    note = get_object_or_404(Note, id=note_id, author=request.user)
    email_id = note.email.id

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('email_notes', email_id=email_id)

    context = {
        'note': note,
        'email': note.email,
    }
    return render(request, 'mail_management/delete_note.html', context)

@login_required
def graphql_playground(request):
    """GraphQL playground for testing queries"""
    return render(request, 'mail_management/graphql_playground.html')

# Web-based authentication views
def web_login(request):
    """Web-based login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            from django.contrib.auth import authenticate, login
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both username and password.')

    return render(request, 'mail_management/auth/login.html')

def web_register(request):
    """Web-based registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validation
        if not all([username, email, password1, password2, first_name, last_name]):
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )

                # Log in the user
                from django.contrib.auth import login
                login(request, user)

                messages.success(request, f'Account created successfully! Welcome, {user.get_full_name()}!')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, 'Failed to create account. Please try again.')

    return render(request, 'mail_management/auth/register.html')

def web_logout(request):
    """Web-based logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('web_login')
