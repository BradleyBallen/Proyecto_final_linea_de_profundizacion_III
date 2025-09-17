from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Level(models.Model):
    CEFR_CHOICES = (
        ('A1','A1'),
        ('A2','A2'),
        ('B1','B1'),
        ('B2','B2'),
        ('C1','C1'),
        ('C2','C2'),
    )
    code = models.CharField(max_length=2, choices=CEFR_CHOICES, unique=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code

class Lesson(models.Model):
    level = models.ForeignKey(Level, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level','order']

    def __str__(self):
        return f"{self.level.code} - {self.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.ForeignKey(Level, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    membership_date = models.DateField(default=timezone.now)
    bio = models.TextField(blank=True)
    is_tutor = models.BooleanField(default=False)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return self.user.username

class LevelMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='level_memberships')
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    SENDER_CHOICES = (('user','user'), ('assistant','assistant'), ('system','system'))
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user','lesson')

