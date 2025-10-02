from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, RegisterView, blacklist_refresh, send_otp_view, verify_otp_view

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/token/blacklist/", blacklist_refresh, name="token_blacklist"),
    path("auth/send-otp/", send_otp_view, name="send_otp"),
    path("auth/verify-otp/", verify_otp_view, name="verify_otp"),
]

