from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Email, Category, Note, UserAction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('password',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class EmailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_names = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Email
        fields = '__all__'
        read_only_fields = ('user', 'received_at')

    def get_category_names(self, obj):
        return obj.get_category_names()

    def get_unread_count(self, obj):
        if hasattr(obj, 'user'):
            return obj.user.get_unread_emails_count()
        return 0

class NoteSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Note content must be at least 10 characters long."
            )
        return value

class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = '__all__'
