from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
            return self.name

class EmailOTP(models.Model):
    email = models.EmailField(db_index=True)
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["email", "-created_at"])
        ]

    def check_otp(self, plain_otp):
        if self.used:
            return False

        if timezone.now() > self.expires_at:
            self.used = True
            return False

        return check_password(plain_otp, self.otp_hash)
