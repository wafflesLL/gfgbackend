from .serializers import RegisterSerializer
from .models import Item
from .serializers import ItemSerializer
from rest_framework_simplejwt.views import token_blacklist
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone 
from django.conf import settings
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .otp_utils import create_and_send_otp
from .models import EmailOTP

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by("-created_at")
    serializer_class = ItemSerializer

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def blacklist_refresh(request):
    refresh = request.data.get("refresh")
    if not refresh:
        return Response({"detail": "refresh required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh)
        token.blacklist()
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_205_RESET_CONTENT)

@api_view(["POST"])
@permission_classes([])
def send_otp_view(request):
    serializer = SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]

    otp_obj, err = create_and_send_otp(email, request=request)
    if err == "cooldown":
        return Response({"detail": "OTP recently sent. Try again later."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)

    return Response({"detail": "OTP sent if the email is valid."},
                    status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([])
def verify_otp_view(request):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    code = serializer.validated_data["code"].strip()

    otp_qs = EmailOTP.objects.filter(email=email, used=False).order_by("-created_at")
    otp_obj = otp_qs.first()
    if not otp_obj:
        return Response({"detail": "Invalid or expired code."},
                        status=status.HTTP_400_BAD_REQUEST)

    if timezone.now() > otp_obj.expires_at:
        return Response({"detail": "Code expired."},
                        status=status.HTTP_400_BAD_REQUEST)

    max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 5)
    if otp_obj.attempts >= max_attempts:
        return Response({"detail": "Too many attempts; request a new code."},
                        status=status.HTTP_400_BAD_REQUEST)

    from django.contrib.auth.hashers import check_password
    if check_password(code, otp_obj.otp_hash):
        otp_obj.used = True
        otp_obj.save(update_fields=["used"])
        return Response({"detail": "OTP verfied."},
                        status=status.HTTP_200_OK)
    else:
        otp_obj.attempts += 1
        otp_obj.save(update_fields=["attempts"])
        return Response({"detail": "Invalid code."},
                        status=status.HTTP_400_BAD_REQUEST)
