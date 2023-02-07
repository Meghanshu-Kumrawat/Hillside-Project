from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from accounts.models import User, Address

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'date_of_birth']  

class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'password', 'password2')

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'], phone=validated_data['phone'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'zip_code', 'full_address']

class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['zip_code', 'full_address']

    def create(self, validated_data):
        user = self.context['request'].user
        address = Address.objects.create(user=user, **validated_data)
        return address