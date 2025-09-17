from django.utils import timezone
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

    import os
    import google.generativeai as genai
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import permissions, status
    from django.utils import timezone
    from .models import Conversation, Message

    # Config Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    class ChatAPIView(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def post(self, request, *args, **kwargs):
            user = request.user
            text = request.data.get('message')
            conversation_id = request.data.get('conversation_id')

            if not text:
                return Response({"detail": "Falta campo 'message'."}, status=status.HTTP_400_BAD_REQUEST)

            # obtener nivel del perfil
            try:
                level = user.profile.level
            except:
                level = None

            # obtener/crear conversación
            if conversation_id:
                conv = Conversation.objects.filter(id=conversation_id, user=user).first()
                if not conv:
                    return Response({"detail": "Conversation not found or not yours."}, status=404)
            else:
                conv = Conversation.objects.create(
                    user=user,
                    level=level,
                    title=f"Chat {user.username} {timezone.now().date()}"
                )

            # guardar mensaje del usuario
            Message.objects.create(conversation=conv, sender="user", text=text)

            # preparar prompt base
            system_prompt = f"""
            You are an English tutor AI assistant. Adapt responses to CEFR level: {level.code if level else "unknown"}.
            Use examples, short exercises, and vocabulary appropriate to the level.
            """

            # concatenar historial (simple, texto plano)
            past_messages = "\n".join(
                [f"{m.sender.upper()}: {m.text}" for m in conv.messages.order_by("created_at")]
            )
            full_prompt = f"{system_prompt}\n\nConversation:\n{past_messages}\n\nUSER: {text}\nASSISTANT:"

            try:
                response = genai.GenerativeModel(MODEL).generate_content(full_prompt)
                assistant_text = response.text.strip()
            except Exception as e:
                return Response({"detail": "Error calling Gemini", "error": str(e)}, status=500)

            # guardar respuesta
            Message.objects.create(conversation=conv, sender="assistant", text=assistant_text)

            return Response({
                "conversation_id": conv.id,
                "response": assistant_text
            })


