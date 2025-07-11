from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Email, Category, Note, UserAction

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_staff')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_admin', 'preferences')}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'user', 'priority', 'is_read', 'received_at')
    list_filter = ('priority', 'is_read', 'received_at', 'categories')
    search_fields = ('subject', 'sender', 'body')
    filter_horizontal = ('categories',)
    readonly_fields = ('received_at',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('email', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'email__subject')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'action_type', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'email__subject')
    readonly_fields = ('timestamp',)
