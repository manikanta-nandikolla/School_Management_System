import random
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    otp = generate_otp()
    user.otp_code = otp
    user.otp_created_at = now()
    user.save()

    subject = "Your OTP Verification Code"
    message = f"Dear {user.get_full_name()},\n\nYour OTP code is: {otp}\n\nUse this to verify your account."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])