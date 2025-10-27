from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
import os

def login_with_otp_success(user):
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response({"message": "Login successful"})
    response.set_cookie("access_token", access, httponly=True, max_age=300)  # 5 Min
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=7*24*60*60) # 7 days
    return response

User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        load_dotenv()
        api_key = os.getenv("GOOGLE_CLIENT_ID")
        token = request.data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(),api_key)

            email_address = idinfo["email"]
            full_name = idinfo.get("name", "")
            
            # Create or get user
            user= User.objects.get(email_address=email_address)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {"email": email_address, "name": user.full_name}
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
