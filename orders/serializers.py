from rest_framework import serializers
from products.serializers import ProductBaseSerializer, ProductColorSerializers, ProductSizeSerializers
from orders.models import Cart
from accounts.serializers import UserBaseSerializer

class CartSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)
    product = ProductBaseSerializer(read_only=True)
    color = ProductColorSerializers(read_only=True)
    size = ProductSizeSerializers(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'color', 'size', 'quantity', 'created_at']

class CartWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'product', 'color', 'size', 'quantity']

    def to_representation(self, instance):
        serializer = CartSerializer(instance, context=self.context)
        return serializer.data


