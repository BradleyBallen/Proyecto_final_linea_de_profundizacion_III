from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Level, Lesson, UserProfile, LevelMembership, Conversation, Message, Progress

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id','code','name','description']

class LessonSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    level_id = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all(), source='level', write_only=True)
    class Meta:
        model = Lesson
        fields = ['id','level','level_id','title','content','order','created_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','password']
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    level = LevelSerializer(read_only=True)
    level_id = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all(), source='level', write_only=True, required=False)
    class Meta:
        model = UserProfile
        fields = ['id','user','level','level_id','membership_date','bio','is_tutor','avatar_url']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        return super().update(instance, validated_data)

class LevelMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    class Meta:
        model = LevelMembership
        fields = ['id','user','level','start_date','end_date']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id','conversation','sender','text','created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ['id','user','level','title','created_at','updated_at','messages']

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['id','user','lesson','completed','score','completed_at']
