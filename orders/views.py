from rest_framework import views, viewsets, generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from orders.models import Cart, Order, Payment
from orders.serializers import CartSerializer, CartWriteSerializer, OrderSerializer

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
    def get(self, request):
        order = Order.objects.get(user=request.user, ordered=False)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


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