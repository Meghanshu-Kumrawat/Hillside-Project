from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import User, Address

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'email', 'date_of_birth']  

class UserPhoneSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
            required=True,
            max_length=13,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'password')
        

class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'password')
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'zip_code', 'full_address']

class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user', 'zip_code', 'full_address']
