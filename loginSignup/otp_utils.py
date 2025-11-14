import random
from twilio.rest import Client
from django.conf import settings

def generate_otp():
    return random.randint(100000, 999999)

otps = {

}

def already_sent_otp(user):
    return str(user.mobile_number) in otps

def send_otp_sms(user):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    otp = generate_otp() 
    number = str(user.mobile_number)
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=number,
    )
    otps[number] = otp
    return otp  

def resend_otp_sms(user):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    otp = otps[user.mobile_number]
    number = str(user.mobile_number)
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=number,
    )
    return otp 

def verify_otp_sms(user, token):
    if str(otps[user.mobile_number]) == str(token):
        otps.clear()
        return True
    return False

