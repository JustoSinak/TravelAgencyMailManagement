import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from .models import Email, Category, Note, UserAction

class EmailType(DjangoObjectType):
    class Meta:
        model = Email
        fields = '__all__'

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = '__all__'

class NoteType(DjangoObjectType):
    class Meta:
        model = Note
        fields = '__all__'

class UserActionType(DjangoObjectType):
    class Meta:
        model = UserAction
        fields = '__all__'

class Query(graphene.ObjectType):
    emails = graphene.List(
        EmailType, 
        search=graphene.String(),
        category_id=graphene.ID(),
        is_read=graphene.Boolean()
    )
    email = graphene.Field(EmailType, id=graphene.ID())
    categories = graphene.List(CategoryType)
    notes = graphene.List(NoteType, email_id=graphene.ID())
    user_actions = graphene.List(UserActionType)
    
    def resolve_emails(self, info, search=None, category_id=None, is_read=None, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        queryset = Email.objects.filter(user=user)
        
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) | 
                Q(body__icontains=search) |
                Q(sender__icontains=search)
            )
        
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
            
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
            
        return queryset.order_by('-received_at')
    
    def resolve_email(self, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return None
        return Email.objects.filter(user=user, id=id).first()
    
    def resolve_categories(self, info, **kwargs):
        return Category.objects.all()
    
    def resolve_notes(self, info, email_id=None, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        queryset = Note.objects.filter(email__user=user)
        if email_id:
            queryset = queryset.filter(email_id=email_id)
        return queryset.order_by('-created_at')
    
    def resolve_user_actions(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return []
        return UserAction.objects.filter(user=user).order_by('-timestamp')

class CreateNote(graphene.Mutation):
    class Arguments:
        email_id = graphene.ID(required=True)
        content = graphene.String(required=True)
    
    note = graphene.Field(NoteType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, email_id, content):
        user = info.context.user
        if not user.is_authenticated:
            return CreateNote(success=False, errors=['Authentication required'])
        
        if len(content.strip()) < 10:
            return CreateNote(
                success=False, 
                errors=['Note content must be at least 10 characters long']
            )
        
        try:
            email = Email.objects.get(id=email_id, user=user)
            note = Note.objects.create(
                email=email,
                author=user,
                content=content
            )
            return CreateNote(note=note, success=True, errors=[])
        except Email.DoesNotExist:
            return CreateNote(success=False, errors=['Email not found'])

class MarkEmailAsRead(graphene.Mutation):
    class Arguments:
        email_id = graphene.ID(required=True)
    
    email = graphene.Field(EmailType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, email_id):
        user = info.context.user
        if not user.is_authenticated:
            return MarkEmailAsRead(success=False, errors=['Authentication required'])
        
        try:
            email = Email.objects.get(id=email_id, user=user)
            email.mark_as_read()
            
            # Record user action
            UserAction.objects.create(
                user=user,
                email=email,
                action_type='OPEN'
            )
            
            return MarkEmailAsRead(email=email, success=True, errors=[])
        except Email.DoesNotExist:
            return MarkEmailAsRead(success=False, errors=['Email not found'])

class Mutation(graphene.ObjectType):
    create_note = CreateNote.Field()
    mark_email_as_read = MarkEmailAsRead.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
