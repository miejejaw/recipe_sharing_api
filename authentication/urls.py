from django.urls import path
from authentication import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/login', views.LoginView.as_view(), name='token-obtain-pair'),
    path('auth/login/refresh-token', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/forgot-password/<str:email>', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
    path('auth/verify-email/<str:token>', views.VerifyEmailView.as_view(), name='verify-email'),
]
