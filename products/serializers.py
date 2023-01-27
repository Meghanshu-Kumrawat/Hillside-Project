from rest_framework import serializers
from products.models import Product, ProductImage, ProductSize, ProductColor, Review
from accounts.serializers import UserBaseSerializer

class ProductImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'caption']


class ProductImageWriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'caption']
        
    def create(self, validated_data):
        product = Product.objects.get(id=self.context['pk'])
        productimage = ProductImage.objects.create(product=product, **validated_data)
        return productimage

class ProductSizeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'quantity']

class ProductSizeWriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'product', 'name', 'quantity']

class ProductColorSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'name']

class ProductColorWriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'product', 'name']

class ReviewSerializers(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'title', 'text', 'rating', 'created_at']

class ReviewWriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'title', 'text', 'rating', 'created_at']


class ProductSerializers(serializers.ModelSerializer):
    productimage_set = ProductImageSerializers(many=True, read_only=True)
    productsize_set = ProductSizeSerializers(many=True, read_only=True)
    productcolor_set = ProductColorSerializers(many=True, read_only=True)
    review_set = ReviewSerializers(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'description', 'material', 'origin', 'price', 'created_at', 'productimage_set', 'productsize_set', 'productcolor_set', 'review_set']

