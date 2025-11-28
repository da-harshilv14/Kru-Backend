from django.urls import path
from . import views
from .auth_utils import GoogleLoginView


urlpatterns = [

    # ---------------------------------------------------------
    # Signup (Email + Mobile OTP Flow)
    # ---------------------------------------------------------
    path("signup/", views.UserSignupView.as_view(), name="signup"),
    path("verify-email/", views.verify_email, name="verify-email"),
    path("verify-mobile-otp/", views.verify_mobile_otp, name="verify-mobile-otp"),
    path("resend-email-otp/", views.resend_email_otp),
    path("resend-mobile-otp/", views.resend_mobile_otp),


    # ---------------------------------------------------------
    # Mobile OTP Login
    # ---------------------------------------------------------
    path("login/", views.LoginOtpView.as_view(), name="login"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),

    # ---------------------------------------------------------
    # Email + Password Login (JWT)
    # ---------------------------------------------------------
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),

    # ---------------------------------------------------------
    # Forgot Password (Email OTP)
    # ---------------------------------------------------------
    path("forgot-password/", views.forgot_password_send_otp, name="forgot-password-send"),
    path("forgot-password/verify-otp/", views.forgot_password_verify_otp, name="forgot-password-verify"),
    path("forgot-password/reset-password/", views.forgot_password_reset, name="forgot-password-reset"),

    # ---------------------------------------------------------
    # Google OAuth Login
    # ---------------------------------------------------------
    path("auth/google/callback/", GoogleLoginView.as_view(), name="google-login"),

    # ---------------------------------------------------------
    # Account Management
    # ---------------------------------------------------------
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.change_password, name="change-password"),
]
