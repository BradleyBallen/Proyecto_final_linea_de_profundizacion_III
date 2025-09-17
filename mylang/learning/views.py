import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from .models import Conversation, Message, UserProfile

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
            level = user.userprofile.level
        except UserProfile.DoesNotExist:
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

        # concatenar historial (solo últimos 10 mensajes para eficiencia)
        past_messages = "\n".join(
            [f"{m.sender.upper()}: {m.text}" for m in conv.messages.order_by("created_at")[:10]]
        )
        full_prompt = f"{system_prompt}\n\nConversation:\n{past_messages}\n\nUSER: {text}\nASSISTANT:"

        try:
            model = genai.GenerativeModel(MODEL)
            response = model.generate_content(full_prompt)
            assistant_text = response.candidates[0].content.parts[0].text.strip()
        except Exception as e:
            return Response({"detail": "Error calling Gemini", "error": str(e)}, status=500)

        # guardar respuesta
        Message.objects.create(conversation=conv, sender="assistant", text=assistant_text)

        return Response({
            "conversation_id": conv.id,
            "response": assistant_text
        })


