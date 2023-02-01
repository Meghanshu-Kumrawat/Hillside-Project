from rest_framework import views, viewsets, generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from orders.models import Cart, Order, Payment
from orders.serializers import CartSerializer, CartWriteSerializer, OrderSerializer

class CartViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset  = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CartSerializer
        return CartWriteSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)

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
            print(cart, '------------------')
            order.product.add(cart)
        order.total = total
        order.save()
        serializer = self.get_serializer(queryset, many=True)

        return Response({"data":serializer.data, "total":total})

class OrderCheckoutViewSet(views.APIView):
    def get(self, request):
        order = Order.objects.get(user=request.user, ordered=False)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)