from rest_framework import views, viewsets, generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.conf import settings
from orders.models import Cart, Order, Payment
from orders.serializers import CartSerializer, CartWriteSerializer, OrderSerializer, PaymentSerializer
import stripe

from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer,
    extend_schema_view, extend_schema, inline_serializer, extend_schema_serializer, OpenApiExample
)

@extend_schema(tags=['cart'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a paginated list of cart products according to query parameters (10 products per page)',
        responses={
            '200': CartSerializer,
        }),
    create=extend_schema(
        summary='Method creates a new cart product',
        request=CartWriteSerializer,
        responses={
            '201': CartSerializer,
        }),
    retrieve=extend_schema(
        summary='Method returns details of a specific cart product',
        responses={
            '200': CartSerializer,
        }),
    destroy=extend_schema(
        summary='Method deletes a specific cart product',
        responses={
            '204': OpenApiResponse(description='The cart product has been deleted'),
        }),
    partial_update=extend_schema(
        summary='Methods does a partial update of chosen fields in a cart product',
        request=CartWriteSerializer,
        responses={
            '200': CartWriteSerializer,
        }),
    update=extend_schema(
        summary='Methods does a update of chosen fields in a cart product',
        request=CartWriteSerializer,
        responses={
            '200': CartWriteSerializer,
        })
)
class CartViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset  = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CartSerializer
        return CartWriteSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)

@extend_schema(tags=['order confirmation'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a summary of cart products to buy.',
        responses={
            '200': CartSerializer,
        })
)
class OrderConfirmationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset  = self.queryset.filter(user=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        order, created = Order.objects.get_or_create(user=request.user, ordered=False)
        total = 0
        for cart in queryset:
            total += cart.product.price * cart.quantity
            order.product.add(cart)
        order.total = total
        order.save()
        serializer = self.get_serializer(queryset, many=True)

        return Response({"data":serializer.data, "total":total})

@extend_schema(tags=['order checkout'])
@extend_schema_view(
    list=extend_schema(
        summary='Method to create a checkout.',
        responses={
            '200': OrderSerializer,
        })
)
class OrderCheckoutViewSet(views.APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        test_payment_intent = stripe.PaymentIntent.create(
        amount=1000, currency='pln', 
        payment_method_types=['card'],
        receipt_email='test@example.com')
        return Response(status=status.HTTP_200_OK, data=test_payment_intent)
        # if 'stripeToken' not in request.data:
        #     return Response({"error": "Stripe token is required."}, status=status.HTTP_400_BAD_REQUEST)
        # order = Order.objects.get(user=request.user, ordered=False)
        # # try:
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        # charge = stripe.Charge.create(
        #     amount=order.total,
        #     currency="inr",
        #     source=request.data['stripeToken'],
        # )
        # print('-------------charge object', charge)
        # if charge:
        #     Payment.objects.create(
        #         amount=order.total,
        #         stripe_charge_id=charge.id,
        #         user=request.user
        #     )
        #     order.ordered = True
        #     return Response({"message": "Payment successful."}, status=status.HTTP_200_OK)
        # except stripe.error.StripeError as e:
        #     return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

class SaveViewSet(views.APIView):
    def post(self, request):
        data = request.data
        email = data['email']
        payment_method_id = data['payment_method_id']
        extra_msg = '' # add new variable to response message  # checking if customer with provided email already exists
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer_data = stripe.Customer.list(email=email).data   
        
        # if the array is empty it means the email has not been used yet  
        if len(customer_data) == 0:
            # creating customer
            customer = stripe.Customer.create(
            email=email)  
        else:
            customer = customer_data[0]
            extra_msg = "Customer already existed."  
            stripe.Charge.create(
                customer=customer, 
                currency='inr', # you can provide any currency you want
                amount=999,
                description='Test payment',
                confirm=True)  
            return Response(status=status.HTTP_200_OK, data={'message': 'Success', 'data': {'customer_id': customer.id, 'extra_msg': extra_msg}})

@extend_schema(tags=['order history'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a order history of previous products.',
        responses={
            '200': OrderSerializer,
        })
)
class OrderHistoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user, ordered=True)
        return queryset