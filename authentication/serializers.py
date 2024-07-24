from rest_framework import serializers
import re
from utils.jwt_token_utils import verify_token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    def validate_password(self, password):
        errors = []   
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lower-case letter.")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one upper-case letter.")
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit.")
        if not re.search(r'[@_!#$%^&*()<>?/\|}{~:=+-.,\[\]]', password):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise serializers.ValidationError(errors)
            
        return password
      
    def validate(self, data):
        
        try:
            token = data.get('token')
            user = verify_token(token, 'password_reset')
            self.user = user
            return data
        except:
            raise serializers.ValidationError({"token": "Token get expired or invalid token, please request a new one."})
            
    def save(self):
        password = self.validated_data['password']
        self.user.set_password(password)
        self.user.save()