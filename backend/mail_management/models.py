from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    preferences = models.JSONField(default=dict)

    def get_unread_emails_count(self):
        return self.emails.filter(is_read=False).count()

    def get_recent_emails(self, limit=10):
        return self.emails.order_by('-received_at')[:limit]

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Email(models.Model):
    PRIORITY_CHOICES = [
        ('H', 'High'),
        ('M', 'Medium'),
        ('L', 'Low'),
    ]

    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.EmailField()
    received_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    categories = models.ManyToManyField(Category, related_name='emails')
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')

    class Meta:
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['sender']),
            models.Index(fields=['received_at']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_read']),
        ]
        ordering = ['-received_at']

    def __str__(self):
        return self.subject

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_category_names(self):
        return [category.name for category in self.categories.all()]

class Note(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(validators=[MinLengthValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note by {self.author} on {self.email}"

    def clean(self):
        if len(self.content.strip()) < 10:
            raise ValidationError('Note content must be at least 10 characters long.')

class UserAction(models.Model):
    ACTION_TYPES = [
        ('OPEN', 'Email opened'),
        ('REPLY', 'Email replied'),
        ('DELETE', 'Email deleted'),
        ('CATEGORY', 'Category changed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user} {self.action_type} {self.email}"
