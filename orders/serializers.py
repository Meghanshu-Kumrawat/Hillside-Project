from rest_framework import serializers
from django.db.models import F, Sum
from products.serializers import ProductBaseSerializer, ProductColorSerializers, ProductSizeSerializers
from orders.models import Cart, Order, Payment
from accounts.serializers import UserBaseSerializer

class CartSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)
    product = ProductBaseSerializer(read_only=True)
    color = ProductColorSerializers(read_only=True)
    size = ProductSizeSerializers(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'color', 'size', 'quantity', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

    def get_total(self, obj):
        return obj.items.annotate(per_item_price=F('price')*F('quantity')).annotate(total=Sum('per_item_price')).values('total')

class CartWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['product', 'color', 'size']

    def to_representation(self, instance):
        serializer = CartSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(user=user, **validated_data)
        if not created:
            cart.quantity += 1
            cart.save()
        return cart

class OrderSerializer(serializers.ModelSerializer):
    product = CartSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['user', 'product', 'delivery_type', 'phone', 'email', 'date', 'from_time', 'to_time', 'created_at', 'ordered_at', 'total', 'payment', 'ordered', 'received']