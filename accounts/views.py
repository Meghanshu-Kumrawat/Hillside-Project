from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from accounts.models import User
from accounts.serializers import UserBaseSerializer, UserPhoneSerializer, UserEmailSerializer
from accounts.verification import GenerateOTP, SendSMS
from accounts.backends import authenticate
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm



class HelloView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        content = {'message': 'Hello, ' + request.user.username}
        return Response(content)


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
                        SendSMS(request.data.get('phone'), msg)

                    return Response({"token":token.key, "message": "your otp is send in email or phone, verify to use the app!"}, status=200)
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
            print(user)
            user.is_active = True
            user.save()
            serializer = UserBaseSerializer(user)
            json = serializer.data
            json['token'] = user.auth_token.key
            return Response({"data":json, "message":"You are authorised!, use same token to access the site!"}, status=200)
        return Response({"error": "OTP is wrong/expired"}, status=400)

class UserLoginView(APIView):
    """ 
    Login the user. 
    """
    def post(self, request, format='json'):
        if request.data.get('email'):
            username = request.data.get('email')
        elif request.data.get('phone'):
            username = request.data.get('phone')
        else:
            return Response({"error":"Please enter the correct email address or phone number and password of your account. Note that both fields may be case-sensitive.!"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=request.data.get('password'))
        if user:
            if user.is_active:
                token = Token.objects.get(user=user).key
                return Response({"user":user.username, "token": token}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message": "Account not active!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "Incorrect Login credentials"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request, format='json'):
        if request.data.get('email'):
            email = request.data.get('email')
            user = User.objects.get(email=email)
        elif request.data.get('phone'):
            phone = request.data.get('phone')
            user = User.objects.get(phone=phone)
        else:
            return Response({"error":"Please enter the correct email address or phone number and password of your account. Note that both fields may be case-sensitive.!"}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))
            if request.data.get('email'):
                send_mail(
                    subject = 'Password reset',
                    message = f'Use this link to reset your password: {reset_link}',
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [request.data.get('email')],
                    fail_silently=False,
                )
            elif request.data.get('phone'):
                msg = f"Password reset\n Use this link to reset your password: {reset_link}"
                SendSMS(request.data.get('phone'), msg)

            return Response({'message': 'Password reset email or sms sent to your registered email or phone!'},)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token, format='json'):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.data)
            if form.is_valid():
                form.save()
                # login the user
                # login(request, user)
                return Response({'message': 'Password reset successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid reset link!'}, status=status.HTTP_400_BAD_REQUEST)