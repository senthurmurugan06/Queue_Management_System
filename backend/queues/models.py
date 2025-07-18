from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Queue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Token(models.Model):
    queue = models.ForeignKey(Queue, related_name='tokens', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('waiting', 'Waiting'), ('serving', 'Serving'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('queue', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Token {self.number} in {self.queue.name}"

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at
