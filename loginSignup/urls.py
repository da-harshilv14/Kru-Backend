from django.urls import path
from . import views
from .auth_utils import GoogleLoginView

urlpatterns = [
    path("signup/", views.UserSignupView.as_view(), name="signup"),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/", views.LoginOtpView.as_view(), name="login"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/google/callback/", GoogleLoginView.as_view(), name="google-login"),
    path('forgot-password/', views.forgot_password_send_otp),
    path('forgot-password/verify-otp/', views.forgot_password_verify_otp),
    path('forgot-password/reset-password/', views.forgot_password_reset),
]
