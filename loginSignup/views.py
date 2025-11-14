from rest_framework import generics, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .otp_utils import send_otp_sms, verify_otp_sms, already_sent_otp, resend_otp_sms
from .serializers import UserSignupSerializer
from .models import User, PasswordResetOTP
import random

otp = ""


User = get_user_model()


@api_view(["GET"])
def test_email(request):
    try:
        send_mail(
            subject="Test Email",
            message="Hello, this is a test from Django using Brevo SMTP!",
            from_email=settings.DEFAULT_FROM_EMAIL,  # uses DEFAULT_FROM_EMAIL
            recipient_list=["harshilvasava8148@gmail.com"],
        )
        return Response({"message": "Email sent successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def forgot_password_send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.update_or_create(
        user=user,
        defaults={"otp": otp}
    )

    subject = "E-mail verification"
    message = f'Your OTP is {otp}, please do not share it with anyone'

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
        return Response({"success": "Email sent successfully!"})
    except Exception as e:
        return Response({"error": f"Error sending email: {e}"}, status=500) 


@api_view(['POST'])
def forgot_password_verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return HttpResponse("Email and OTP required.", status=400)

    try:
        user = User.objects.get(email_address=email)
        otp_obj = PasswordResetOTP.objects.get(user=user)

        if otp_obj.otp != otp:
            return HttpResponse("Invalid OTP.", status=400)

        return HttpResponse("OTP verified successfully.")
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)
    except PasswordResetOTP.DoesNotExist:
        return HttpResponse("No OTP found for this user.", status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Allows the logged-in user to change their password.
    Expected fields: old_password, new_password, confirm_password
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    # 🧩 Validation
    if not old_password or not new_password or not confirm_password:
        return Response(
            {"error": "All fields (old_password, new_password, confirm_password) are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    if old_password == new_password:
        return Response({"error": "New password cannot be same as old password."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def forgot_password_reset(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'error': 'Email and new password required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    user.password = make_password(new_password)
    user.save()

    PasswordResetOTP.objects.filter(user=user).delete()

    return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []  


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # extra fields you want in response
        token["full_name"] = user.full_name
        token["email_address"] = user.email_address
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "user": {
                "id": self.user.id,
                "email": self.user.email_address,
                "full_name": self.user.full_name,
                "role": self.user.role
            }
        })
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email_address")
        password = request.data.get("password")
        role = request.data.get("role")
        remember_me = request.data.get("remember", False)

        if not email or not password or not role:
            return Response({"error": "Email, password and role are required"}, status=400)

        # Check email exists
        try:
            user = User.objects.get(email_address=email)
        except User.DoesNotExist:
            return Response({"error": "Email not registered"}, status=404)

       
        # Check role
        if user.role != role.lower():
            return Response({"error": "Role does not match this email"}, status=400)

        # Check password
        if not user.check_password(password):
            return Response({"error": "Incorrect password. Please try again."}, status=400)

        # now call parent to generate tokens
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            data = response.data
            refresh = data.get("refresh")
            access = data.get("access")

            access_max_age = 300   # default 5 mins
            refresh_max_age = 7*24*60*60

            if remember_me:
                access_max_age = 86400
                refresh_max_age = 30*24*60*60

            response.set_cookie("access_token", access, httponly=True, secure=True, samesite="None", max_age=access_max_age)
            response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="None", max_age=refresh_max_age)

            response.data = {
                "message": "Login successful",
                "user": data.get("user", {}),
            }

        return response


class CookieTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=300,   
            )
            return response

        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginOtpView(APIView):
    def post(self, request):
        mobile_number = request.data.get("mobile_number")
        try:
            user = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return Response({"error": f"User with mobile number {mobile_number} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if already_sent_otp(user):
            otp = resend_otp_sms(user)
            return Response({"message": f"OTP sent to {mobile_number}", "user_id": user.id})
        else:
            otp = send_otp_sms(user)
            return Response({"message": f"OTP sent to {mobile_number}", "user_id": user.id})


class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        token = request.data.get("otp")
        remember = request.data.get("remember", False)  # new

        try:
            user = User.objects.get(id=user_id)
            if verify_otp_sms(user, token):
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                refresh_token = str(refresh)

                # Set token lifetimes
                access_max_age = 300  # 5 minutes
                refresh_max_age = 7*24*60*60  # 7 days

                if remember:
                    access_max_age = 60*60*24  # 1 day
                    refresh_max_age = 30*24*60*60  # 30 days

                response = Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'email': user.email_address,
                        'full_name': user.full_name,
                        'role': user.role
                    }
                }, status=status.HTTP_200_OK)
                
                # Set cookies with proper settings
                response.set_cookie(
                    'access_token',
                    access,
                    httponly=True,
                    secure=True,  # Set to True in production with HTTPS
                    samesite="None",
                    max_age=access_max_age,
                )
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="None",
                    max_age=refresh_max_age,
                )

                return response

            else:
                return Response({"error": "Invalid OTP. Please try again"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        # Delete both cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response