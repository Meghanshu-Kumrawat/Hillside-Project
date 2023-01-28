from rest_framework import views, viewsets, generics, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from orders.models import Cart
from orders.serializers import CartSerializer, CartWriteSerializer

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

