import time
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from .models import OTP
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

OTP_EXPIRY_SECONDS = 300   # 5 min expiry
MAX_ATTEMPTS = 3
APP_NAME = "KrushiSetu"  # Change your app name


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_is_expired(otp_obj):
    return timezone.now() > otp_obj.created_at + timedelta(seconds=OTP_EXPIRY_SECONDS)


def get_or_create_otp(user, purpose):
    otp_obj, created = OTP.objects.get_or_create(
        user=user,
        purpose=purpose,
        defaults={"otp": generate_otp()}
    )

    # regenerate if expired
    if not created and otp_is_expired(otp_obj):
        otp_obj.otp = generate_otp()
        otp_obj.created_at = timezone.now()
        otp_obj.attempts = 0
        otp_obj.save()

    return otp_obj


def send_sms(number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=str(number)
    )


def send_otp(user, purpose):
    otp_obj = get_or_create_otp(user, purpose)
    otp = otp_obj.otp
    user_email = user.email_address

    # --------- SMS for mobile OTP ---------
    if purpose in ("login", "mobile_verify"):
        message = (
            f"Your {APP_NAME} {purpose.replace('_', ' ')} OTP is {otp}. "
            f"It expires in 5 minutes. Do NOT share this with anyone."
        )
        send_sms(user.mobile_number, message)
        return otp

    # --------- EMAIL for other OTP purposes ---------

    # Customize subject/heading/description based on purpose
    purpose_map = {
        "email_verify": {
            "subject": f"{APP_NAME} - Email Verification",
            "heading": "Verify Your Email",
            "description": f"We received a request to verify the email {user_email}."
        },
        "forgot_password": {
            "subject": f"{APP_NAME} - Reset Password OTP",
            "heading": "Reset Your Password",
            "description": f"We received a request to reset your password for {user_email}."
        },
        "account_security": {
            "subject": f"{APP_NAME} - Security Alert",
            "heading": "Secure Your Account",
            "description": "Use the OTP below to secure your account."
        },
        "default": {
            "subject": f"{APP_NAME} - OTP Verification",
            "heading": "OTP Verification",
            "description": "Use this OTP to continue."
        }
    }

    config = purpose_map.get(purpose, purpose_map["default"])

    # Render HTML email
    html_content = render_to_string("otp_email.html", {
        "otp": otp,
        "user_email": user_email,
        "heading": config["heading"],
        "description": config["description"]
    })

    email = EmailMultiAlternatives(
        subject=config["subject"],
        body=f"Your OTP is {otp}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return otp


def verify_otp(user, purpose, received_otp):
    try:
        otp_obj = OTP.objects.get(user=user, purpose=purpose)
    except OTP.DoesNotExist:
        return False, "OTP not generated"

    if otp_is_expired(otp_obj):
        otp_obj.delete()
        return False, "OTP expired"

    if otp_obj.attempts >= MAX_ATTEMPTS:
        otp_obj.delete()
        return False, "Too many invalid attempts. OTP removed."

    if str(otp_obj.otp) != str(received_otp):
        otp_obj.attempts += 1
        otp_obj.save()
        return False, "Invalid OTP"

    # OTP valid → delete it
    otp_obj.delete()
    return True, "OTP verified successfully"
