from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from accounts.serializers import UserBaseSerializer, UserPhoneSerializer, UserEmailSerializer
from accounts.verification import GenerateOTP, sendSMS


class HelloView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        content = {'message': 'Hello, ' + request.user.username}
        return Response(content)


# This class returns the string needed to generate the key


EXPIRY_TIME = 500
class UserRegisterView(APIView):
    """ 
    Register the user. 
    """
    def post(self, request, format='json'):
        if request.data.get('email'):
            serializer = UserEmailSerializer(data=request.data)
        elif request.data.get('phone'):
            serializer = UserPhoneSerializer(data=request.data)
        else:
            return Response({"error":"Please enter the correct email address or phone number and password for a your account. Note that both fields may be case-sensitive.!"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(raise_exception=True):
            if request.data.get('password') == request.data.get('password1'):
                user = serializer.save()

                if user:
                    token = Token.objects.create(user=user)
            
                    keygen = GenerateOTP()
                    OTP = keygen.gererate(token.key)
                    if request.data.get('email'):
                        send_mail(
                            subject='Hillside',
                            message='Your OTP is ' + OTP.now(),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[request.data.get('email')])
                    elif request.data.get('phone'):
                        msg = "Your otp is " + OTP.now()
                        sendSMS(msg, request.data.get('phone'))

                    return Response({"token":token.key, "auth message": "your otp is send in email or phone, verify to use the app!"}, status=200)
            else:
                return Response({"error":"both password needs to be same!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    # This Method verifies the OTP
    @staticmethod
    def post(request):
        token = request.data.get('token')
        otp = request.data.get('otp')
        keygen = GenerateOTP()
        
        if keygen.verify(token, otp):
            user = User.objects.get(auth_token=request.data.get('token'))
            user.is_active = True
            user.save()
            serializer = UserBaseSerializer(user)
            json = serializer.data
            json['token'] = user.auth_token.key
            return Response({"data":json, "message":"You are authorised!, use same token to access the site!"}, status=200)
        return Response({"error": "OTP is wrong/expired"}, status=400)