from rest_framework import generics, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail

from .otp_utils import send_otp, verify_otp
from .serializers import UserSignupSerializer

User = get_user_model()


# --------------------------------------------------------------------
# Forgot Password - Send OTP (Email)
# --------------------------------------------------------------------

@api_view(['POST'])
def forgot_password_send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # IMPORTANT CHANGE ↓↓↓
    send_otp(user, "forgot_password")

    return Response({"success": "OTP sent to your email."})


# --------------------------------------------------------------------
# Forgot Password - Verify OTP
# --------------------------------------------------------------------

@api_view(['POST'])
def forgot_password_verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({"error": "Email and OTP required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    success, msg = verify_otp(user, "forgot_password", otp)
    if not success:
        return Response({"error": msg}, status=400)

    return Response({"message": "OTP verified successfully"})


# --------------------------------------------------------------------
# Forgot Password – Reset
# --------------------------------------------------------------------

@api_view(['POST'])
def forgot_password_reset(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({"error": "Email and new password required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    user.password = make_password(new_password)
    user.save()

    return Response({"message": "Password reset successful"})


# --------------------------------------------------------------------
# Change Password (Authenticated)
# --------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not old_password or not new_password or not confirm_password:
        return Response({"error": "All fields are required."}, status=400)

    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=400)

    if new_password != confirm_password:
        return Response({"error": "New passwords do not match."}, status=400)

    if old_password == new_password:
        return Response({"error": "New password cannot be same as old password."}, status=400)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully!"})


# --------------------------------------------------------------------
# Signup – Step 1 (Send email OTP)
# --------------------------------------------------------------------

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        confirm = request.data.get("confirm_password")

        if password != confirm:
            return Response({"error": "Passwords do not match"}, status=400)

        email = request.data.get("email_address")
        mobile = request.data.get("mobile_number")

        # ---------------------------------------------
        # 1️⃣ Check if user already exists
        # ---------------------------------------------
        existing_user = User.objects.filter(email_address=email).first()
        existing_user1 = User.objects.filter(mobile_number=mobile).first()

        if existing_user or existing_user1:
            if existing_user.is_active:
                # User already fully registered
                return Response(
                    {"error": "Account with email already exists. Please log in."},
                    status=400
                )
            
            if existing_user1.is_active:
                return Response(
                    {"error": "Account with mobile no already exists. Please log in."},
                    status=400
                )

            # ---------------------------------------------
            # 2️⃣ User exists but NOT ACTIVE → resend OTP
            # ---------------------------------------------
            # Update user fields (in case user changed name/mobile)
            existing_user.full_name = request.data.get("full_name")
            existing_user.mobile_number = mobile
            existing_user.set_password(password)
            existing_user.save()

            send_otp(existing_user, "email_verify")

            return Response({
                "message": "Account already exists but is not verified. OTP re-sent to email.",
                "user_id": existing_user.id
            }, status=200)

        # ---------------------------------------------
        # 3️⃣ No user → Create new one
        # ---------------------------------------------
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user.is_active = False
        user.save()

        send_otp(user, "email_verify")

        return Response({
            "message": "Signup successful. Verify your email using the OTP sent to you.",
            "user_id": user.id
        }, status=201)



# --------------------------------------------------------------------
# JWT Login With Email + Password
# --------------------------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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

        try:
            user = User.objects.get(email_address=email)
        except User.DoesNotExist:
            return Response({"error": "Email not registered"}, status=404)

        if user.role != role.lower():
            return Response({"error": "Role does not match this email"}, status=400)

        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=400)

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            tokens = response.data
            refresh = tokens.get("refresh")
            access = tokens.get("access")

            access_age = 300
            refresh_age = 7 * 24 * 3600

            if remember_me:
                access_age = 86400
                refresh_age = 30 * 24 * 3600

            response.set_cookie("access_token", access, httponly=True, secure=True, samesite="None", max_age=access_age)
            response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="None", max_age=refresh_age)

            response.data = {
                "message": "Login successful",
                "user": tokens.get("user", {})
            }

        return response


# --------------------------------------------------------------------
# Refresh token using cookies
# --------------------------------------------------------------------

class CookieTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"error": "No refresh token"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            response = Response({"message": "Token refreshed"})
            response.set_cookie("access_token", access, httponly=True, secure=True, samesite="None", max_age=300)
            return response
        except:
            return Response({"error": "Invalid refresh token"}, status=401)


# --------------------------------------------------------------------
# Login With Mobile OTP (Step 1)
# --------------------------------------------------------------------

class LoginOtpView(APIView):
    def post(self, request):
        mobile = request.data.get("mobile_number")

        try:
            user = User.objects.get(mobile_number=mobile)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        send_otp(user, "login")

        return Response({"message": "OTP sent", "user_id": user.id})


# --------------------------------------------------------------------
# Login With Mobile OTP – Verify (Step 2)
# --------------------------------------------------------------------

class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")
        remember = request.data.get("remember", False)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        success, msg = verify_otp(user, "login", otp)
        if not success:
            return Response({"error": msg}, status=400)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        access_age = 300
        refresh_age = 7 * 24 * 3600

        if remember:
            access_age = 86400
            refresh_age = 30 * 24 * 3600

        response = Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email_address,
                "full_name": user.full_name,
                "role": user.role
            }
        })

        response.set_cookie("access_token", access, httponly=True, secure=True, samesite="None", max_age=access_age)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="None", max_age=refresh_age)

        return response


# --------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------

class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


# --------------------------------------------------------------------
# Signup – Step 2 (Email OTP verification → send mobile OTP)
# --------------------------------------------------------------------

@api_view(['POST'])
def verify_email(request):
    email = request.data.get("email_address")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response({"error": "Email and OTP required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    success, msg = verify_otp(user, "email_verify", otp)
    if not success:
        return Response({"error": msg}, status=400)

    send_otp(user, "mobile_verify")

    return Response({"message": "Email verified. OTP sent to your mobile.", "user_id": user.id})


# --------------------------------------------------------------------
# Signup – Step 3 (Mobile OTP verification → activate)
# --------------------------------------------------------------------

@api_view(['POST'])
def verify_mobile_otp(request):
    user_id = request.data.get("user_id")
    otp = request.data.get("otp")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    success, msg = verify_otp(user, "mobile_verify", otp)
    if not success:
        return Response({"error": msg}, status=400)

    user.is_active = True
    user.save()

    return Response({"message": "Registration completed successfully. You can now login."})


@api_view(['POST'])
def resend_email_otp(request):
    email = request.data.get("email_address")

    if not email:
        return Response({"error": "Email required"}, status=400)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    send_otp(user, "email_verify")

    return Response({"message": "Email OTP resent successfully"})

@api_view(['POST'])
def resend_mobile_otp(request):
    user_id = request.data.get("user_id")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    send_otp(user, "mobile_verify")

    return Response({"message": "Mobile OTP resent successfully"})


