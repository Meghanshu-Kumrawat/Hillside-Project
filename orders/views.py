from rest_framework import views, viewsets, generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.conf import settings
from accounts.models import User, Address
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset  = self.queryset.filter(user=self.request.user, ordered=False)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CartSerializer
        return CartWriteSerializer

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset  = self.queryset.filter(user=self.request.user, ordered=False)
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'payment_method_id' not in request.data or 'address_id' not in request.data:
            return Response({"error": "payment_method_id or address_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            user = User.objects.get(id=request.user.id)
            address = Address.objects.get(id=request.data['address_id'])
            payment_method_id = request.data['payment_method_id']
            stripe.api_key = settings.STRIPE_SECRET_KEY

            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            pay_intent = stripe.PaymentIntent.create(
                customer=customer.id, 
                currency='inr', 
                amount=int(order.total * 100),
                description='Test payment',
                payment_method=payment_method_id,
                receipt_email=user.email,
                metadata={'order_id': order.id, 'user_id': user.id, 'email': user.email, 'name': user.username, 'phone': user.phone},
                confirm=True)  
 
            if pay_intent:
                payment = Payment.objects.create(
                    amount=order.total,
                    stripe_charge_id=pay_intent.id,
                    user=request.user
                )
                order.ordered = True
                order.payment = payment
                order.address = address
                order.phone = request.data.get('phone')
                order.email = request.data.get('email')
                if request.data.get('delivery_type') == 'Personalised':
                    order.delivery_type = 'Personalised'
                    if request.data.get('date') and request.data.get('from_time') and request.data.get('to_time'):
                        order.date = request.data.get('date')
                        order.from_time = request.data.get('from_time')
                        order.to_time = request.data.get('to_time')
                    else:
                        return Response({"error": "date, from_time and to_time is required."}, status=status.HTTP_400_BAD_REQUEST)
                order.save()
                for cart in order.product.all():
                    cart.ordered = True
                    cart.save()
                    cart.product.quantity -= cart.quantity
                    cart.product.save()
                return Response({"message": "Payment successful.", "payment_id":pay_intent.id}, status=status.HTTP_200_OK)
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user, ordered=True)
        return queryset