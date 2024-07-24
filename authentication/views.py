from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from user_management.models import Users
from user_management.serializers import UserSerializer
from utils.email_utils import send_reset_password_email, send_verification_email
from utils.jwt_token_utils import verify_token
from utils.format_errors import validation_error
from authentication.serializers import ResetPasswordSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated



class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        auth = JWTAuthentication()
        try:
            user_auth_tuple = auth.authenticate(request)
        except Exception:
            user_auth_tuple = None

        if user_auth_tuple is not None:
            response_data = {
                "status": "FAILED",
                "message": "Forbidden: You are already logged in",
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            response_data = {
                "status": "FAILED",
                "message": "Validation error",
                "errors": validation_error(serializer.errors)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if not user:
            response_data = {
                "status": "FAILED",
                "message": "Wrong email or password",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_verified:
            send_verification_email(user)
            response_data = {
                "status": "FAILED",
                "message": "Please verify your email address, email has been sent.",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role
        
        is_premier = is_user_has_active_package(user)
        
        user_serializer = UserSerializer(user)

        response_data = {
            'status': 'OK',
            'message': 'User logged in successfully.',
            'data':{
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'is_premier': is_premier,
                **user_serializer.data,
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    queryset = Users.objects.all()
    lookup_field = 'email'
    
    def get(self, request, *args, **kwargs):
        user_email = self.kwargs.get('email')
        if not user_email or user_email.strip() == '':
            response_data = {
                "status": "FAILED",
                "message": "Email is required",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.queryset.get(email = user_email)
        except Users.DoesNotExist:
            response_data = {
                "status": "FAILED",
                "message": "User with this email does not exist",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        if not send_reset_password_email(user):
            response_data = {
                "status": "FAILED",
                "message": "An error occurred while sending the email. Please try again later.",
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response_data = {
            "status": "OK",
            "message": "Password reset email has been sent",
        }
        return Response(response_data, status=status.HTTP_200_OK)

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = verify_token(token, 'email_verification')
            user.is_verified = True
            user.save()
            response_data = {
                "status": "OK",
                "message": "Email verified successfully.",
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {
                "status": "FAILED",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            response_data = {
                "status": "FAILED",
                "message": "Validation error",
                "errors": validation_error(serializer.errors)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        response_data = {
            "status": "OK",
            "message": "Password updated successfully",
        }
        return Response(response_data, status=status.HTTP_200_OK)
