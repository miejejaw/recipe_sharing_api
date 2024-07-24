import re
from rest_framework import serializers
from .models import Users

    
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'is_verified', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True}, 
            'id': {'read_only': True},  
            'is_verified': {'read_only': True},
        }

            
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
    
    def save(self, **kwargs):
        user = Users(**self.validated_data)
        user.set_password(self.validated_data['password'])
        user.save()
        return user
 
class UserUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
          
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
        if 'password' in data and data['password']:
            self.validate_password(data['password'])
            
            if 'old_password' not in data or not data['old_password']:
                raise serializers.ValidationError({"old_password": "Old password is required when updating password."})
                
            if not self.instance.check_password(data['old_password']):
                raise serializers.ValidationError({'old_password': "Old password is incorrect."})
        
        return data

    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'old_password', 'is_verified', 'created_at', 'updated_at')
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'password': {'required': False, 'write_only': True, 'allow_blank': True, 'allow_null': True},
            'first_name': {'required': False, 'allow_blank': True, 'allow_null': True},
            'last_name': {'required': False, 'allow_blank': True, 'allow_null': True},
            'user_name': {'required': False, 'allow_blank': True, 'allow_null': True},
            'is_verified': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.date_of_birth = validated_data.get('email', instance.date_of_birth)
        
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
            
        instance.save()
        return instance
    