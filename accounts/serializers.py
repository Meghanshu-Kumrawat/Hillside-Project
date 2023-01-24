from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import User

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'   

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
    
        