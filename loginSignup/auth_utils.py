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
    response.set_cookie("access_token", access, httponly=True, max_age=300)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=7*24*60*60)
    return response

User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("token")

        try:
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                os.getenv("GOOGLE_CLIENT_ID")
            )

            email = idinfo.get("email")
            name = idinfo.get("name", "")

            user, created = User.objects.get_or_create(
                email_address=email,
                defaults={"full_name": name}
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh_token = str(refresh)

            # Cookie expiry times
            access_max_age = 300
            refresh_max_age = 7 * 24 * 60 * 60

            # Create response
            response = Response({
                "message": "Login successful",
                "user": {
                    "email": email,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }, status=status.HTTP_200_OK)

            # 🔥 Set cookies like normal login
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=access_max_age,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=refresh_max_age,
            )

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

