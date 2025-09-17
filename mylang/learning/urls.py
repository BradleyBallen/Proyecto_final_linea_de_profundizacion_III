from rest_framework.routers import DefaultRouter
from .views import (LevelViewSet, LessonViewSet, UserViewSet, UserProfileViewSet,
                    LevelMembershipViewSet, ConversationViewSet, MessageViewSet, ProgressViewSet, ChatAPIView)
from django.urls import path, include

router = DefaultRouter()
router.register(r'levels', LevelViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'memberships', LevelMembershipViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'progress', ProgressViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatAPIView.as_view(), name='chat'),
]
