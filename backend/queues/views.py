from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Queue, Token
from .serializers import QueueSerializer, TokenSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login

class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def move_up(self, request, pk=None):
        token = self.get_object()
        try:
            prev_token = Token.objects.filter(
                queue=token.queue,
                number__lt=token.number
            ).order_by('-number').first()
            
            if prev_token:
                temp_number = token.number
                token.number = prev_token.number
                prev_token.number = temp_number
                token.save()
                prev_token.save()
                return Response({'message': 'Token moved up successfully'})
            else:
                return Response({'error': 'Token is already at the top'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def move_down(self, request, pk=None):
        token = self.get_object()
        try:
            next_token = Token.objects.filter(
                queue=token.queue,
                number__gt=token.number
            ).order_by('number').first()
            
            if next_token:
                temp_number = token.number
                token.number = next_token.number
                next_token.number = temp_number
                token.save()
                next_token.save()
                return Response({'message': 'Token moved down successfully'})
            else:
                return Response({'error': 'Token is already at the bottom'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def assign_top_for_service(self, request):
        queue_id = request.data.get('queue_id')
        if not queue_id:
            return Response({'error': 'queue_id is required.'}, status=400)
        try:
            queue = Queue.objects.get(id=queue_id)
            top_token = Token.objects.filter(queue=queue, status='waiting').order_by('number').first()
            if not top_token:
                return Response({'error': 'No waiting tokens in this queue.'}, status=404)
            Token.objects.filter(queue=queue, status='serving').update(status='waiting')
            top_token.status = 'serving'
            top_token.save()
            return Response({'message': 'Top token assigned for service.', 'token_id': top_token.id})
        except Queue.DoesNotExist:
            return Response({'error': 'Queue not found.'}, status=404)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        token = self.get_object()
        if token.status == 'cancelled':
            return Response({'error': 'Token already cancelled.'}, status=400)
        token.status = 'cancelled'
        token.save()
        return Response({'message': 'Token cancelled successfully.'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    if not username or not password or not email:
        return Response({'error': 'Username, email, and password required.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password, email=email, is_active=False)
    otp = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=10)
    EmailOTP.objects.create(user=user, otp=otp, expires_at=expires_at)
    send_mail(
        'Your OTP Code',
        f'Your OTP code is: {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response({'message': 'User created. Please verify your email with the OTP sent.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    username = request.data.get('username')
    otp = request.data.get('otp')
    try:
        user = User.objects.get(username=username)
        email_otp = user.email_otp
        if email_otp.is_verified:
            return Response({'error': 'OTP already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.is_expired():
            return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.otp != otp:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        email_otp.is_verified = True
        email_otp.save()
        user.is_active = True
        user.save()
        return Response({'message': 'Email verified. You can now log in.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except EmailOTP.DoesNotExist:
        return Response({'error': 'OTP not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not active.'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    active_queues = Queue.objects.filter(tokens__status__in=['waiting', 'serving']).distinct().count()
    total_tokens_today = Token.objects.filter(created_at__gte=today_start).count()
    currently_waiting_tokens = Token.objects.filter(status='waiting').count()
    serving_token = Token.objects.filter(status='serving').order_by('-updated_at').first()
    currently_serving_token = serving_token.number if serving_token else None
    completed_tokens = Token.objects.filter(status='completed', created_at__gte=today_start)
    wait_times = []
    for token in completed_tokens:
        wait_time = (token.updated_at - token.created_at).total_seconds()
        wait_times.append(wait_time)
    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
    queue_length_trends = []
    for hour in range(24):
        hour_start = today_start + timedelta(hours=hour)
        hour_end = hour_start + timedelta(hours=1)
        count = Token.objects.filter(created_at__gte=hour_start, created_at__lt=hour_end).count()
        queue_length_trends.append({'hour': hour, 'count': count})
    return Response({
        'active_queues': active_queues,
        'total_tokens_today': total_tokens_today,
        'currently_waiting_tokens': currently_waiting_tokens,
        'currently_serving_token': currently_serving_token,
        'average_wait_time_seconds': avg_wait_time,
        'queue_length_trends': queue_length_trends,
    })
