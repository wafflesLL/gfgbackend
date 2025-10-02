import secrets
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .models import EmailOTP

def _gen_numeric_otp(length: int):
    max_val = 10**length - 1
    n = secrets.randbelow(max_val + 1)
    return str(n).zfill(length)

def create_and_send_otp(email: str, request=None):
    length = getattr(settings, "OTP_CODE_LENGTH", 6)
    otp = _gen_numeric_otp(length)
    otp_hash = make_password(otp)

    now = timezone.now()
    expires_at = now + timedelta(minutes=getattr(settings, "OTP_EXPIRES_MINUTES", 10))

    last = EmailOTP.objects.filter(email=email).order_by("-created_at").first()
    if last:
        cooldown = getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 60)
        if (now - last.created_at).total_seconds() < cooldown:
            return None, "cooldown"

    otp_obj = EmailOTP.objects.create(
        email=email,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )

    subject = "Your Glasses For Good verification code"
    message = f"Your verification code is: {otp}\nIt will expire at {expires_at.isoformat()}.\nIf you did not request this code, ignore this message."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return otp_obj, None

