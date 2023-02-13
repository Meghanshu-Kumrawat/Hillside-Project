from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from accounts.models import User, Address
from accounts.serializers import UserBaseSerializer, UserEmailSerializer, AddressSerializer, AddressWriteSerializer
from accounts.verification import GenerateOTP
from accounts.backends import authenticate
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q
import stripe

from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer,
    extend_schema_view, extend_schema, inline_serializer, extend_schema_serializer, OpenApiExample
)



class HelloView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        content = {'message': 'Hello, World!', 'user': len(User.objects.all())}
        return Response(content)

class UserRegisterView(APIView):
    """ 
    Register the user. 
    """
    @extend_schema(
            summary="Method to register the user",
            request=UserEmailSerializer,
            responses={
                '200':inline_serializer(name="register",
                    fields={"token": serializers.CharField(), 
                            "message": serializers.CharField()})}
            # more customizations
        )
    def post(self, request, format='json'):
        serializer = UserEmailSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            if user:
                try:
                    token = Token.objects.create(user=user)
            
                    keygen = GenerateOTP()
                    OTP = keygen.gererate(token.key)
                    print("token", token.key, "OTP", OTP.now())
                    
                    send_mail(
                        subject='Hillside',
                        message='Your OTP is ' + OTP.now(),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[request.data.get('email')])

                    return Response({"token":token.key, "message": "your otp is send in email, verify to use the app!"}, status=200)
                except Exception as e:
                    user.delete()
                    token.delete()
                    return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
            summary="Method to modify the user",
            request=UserBaseSerializer,
            responses=UserBaseSerializer
    )
    def patch(self, request):
        serializer = UserBaseSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
            summary="Method to delete the user",
            responses={}
    )
    def delete(self, request):
        user = User.objects.get(id=request.user.id)
        user.delete()
        return Response({"message":"user account deleted successfully!"}, status=status.HTTP_200_OK)

@extend_schema(
    summary="Method to verify the OTP",
    request=inline_serializer(name="verify", fields={"token": serializers.CharField(), "otp": serializers.CharField()}),
    responses={
            '200': UserBaseSerializer,
        }
)
class VerifyOtpView(APIView):
    # This Method verifies the OTP
    @staticmethod
    def post(request):
        token = request.data.get('token')
        otp = request.data.get('otp')
        keygen = GenerateOTP()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        if keygen.verify(token, otp):
            user = User.objects.get(auth_token=request.data.get('token'))
            user.is_active = True
            user.save()
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
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
        email = request.data.get('email')

        user = authenticate(username=email, password=request.data.get('password'))
        if user:
            if user.is_active:
                serializer = UserBaseSerializer(user)
                json = serializer.data
                json['token'] = user.auth_token.key
                return Response({"data":json, "message":"You are authorised!, use same token to access the site!"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message": "Account not active!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"message": "Incorrect Login credentials"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request, format='json'):
        email = request.data.get('email')
        user = User.objects.get(email=email)
        
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

            return Response({'message': 'Password reset email sent to your registered email!'}, status=status.HTTP_200_OK)
        return Response({'error': 'Email is not registered. please create new account!'},)

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

@extend_schema(tags=['address'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a paginated list of address according to query parameters (10 projects per page)',
        responses={
            '200': PolymorphicProxySerializer(component_name='PolymorphicProject',
                serializers=[
                    AddressSerializer, 
                ], resource_type_field_name=None, many=True),
        }),
    create=extend_schema(
        summary='Method creates a new address',
        request=AddressWriteSerializer,
        responses={
            '201': AddressSerializer,
        }),
    retrieve=extend_schema(
        summary='Method returns details of a specific address',
        responses={
            '200': AddressSerializer,
        }),
    destroy=extend_schema(
        summary='Method deletes a specific address',
        responses={
            '204': OpenApiResponse(description='The address has been deleted'),
        }),
    partial_update=extend_schema(
        summary='Methods does a partial update of chosen fields in a address',
        responses={
            '200': AddressSerializer,
        }),
    update=extend_schema(
        summary='Methods does a update of chosen fields in a address',
        responses={
            '200': AddressSerializer,
        })
)
class AddressViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return AddressSerializer
        return AddressWriteSerializer
    