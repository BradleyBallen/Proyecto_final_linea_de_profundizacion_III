from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Level, Lesson, UserProfile, LevelMembership, Conversation, Message, Progress
from .serializers import (LevelSerializer, LessonSerializer, UserSerializer, UserProfileSerializer,
                          LevelMembershipSerializer, ConversationSerializer, MessageSerializer, ProgressSerializer)

# Permisos simples
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (hasattr(obj,'user') and obj.user == request.user) or obj == request.user

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['code','name','description']

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('level').all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['level']
    search_fields = ['title','content']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user','level').all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['level__code']
    search_fields = ['user__username','user__first_name','user__last_name']

class LevelMembershipViewSet(viewsets.ModelViewSet):
    queryset = LevelMembership.objects.select_related('user','level').all()
    serializer_class = LevelMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.prefetch_related('messages').all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user','level','created_at']
    ordering = ['-updated_at']

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProgressViewSet(viewsets.ModelViewSet):
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','lesson','completed']

