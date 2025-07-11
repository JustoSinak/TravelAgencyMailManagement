from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Email, Category, Note, UserAction
from .serializers import EmailSerializer, CategorySerializer, NoteSerializer, UserActionSerializer

class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(email__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class UserActionViewSet(viewsets.ModelViewSet):
    queryset = UserAction.objects.all()
    serializer_class = UserActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

@login_required
def email_catalog(request):
    search_term = request.GET.get('search', '')
    emails = Email.objects.filter(user=request.user)
    if search_term:
        emails = emails.filter(subject__icontains=search_term)
    context = {
        'emails': emails.order_by('-received_at'),
        'search_term': search_term,
    }
    return render(request, 'mail_management/email_catalog.html', context)

@login_required
def email_notes(request, email_id):
    email = get_object_or_404(Email, id=email_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and len(content) >= 10:
            Note.objects.create(email=email, author=request.user, content=content)
            return redirect('email_notes', email_id=email.id)
    notes = email.notes.all().order_by('-created_at')
    context = {
        'email': email,
        'notes': notes,
    }
    return render(request, 'mail_management/email_notes.html', context)
