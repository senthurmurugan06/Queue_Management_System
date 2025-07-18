from rest_framework.routers import DefaultRouter
from .views import QueueViewSet, TokenViewSet, register, verify_otp, dashboard_metrics, custom_login
from django.urls import path

router = DefaultRouter()
router.register(r'queues', QueueViewSet)
router.register(r'tokens', TokenViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('dashboard/metrics/', dashboard_metrics, name='dashboard-metrics'),
    path('custom-login/', custom_login, name='custom-login'),
] 