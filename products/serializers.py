from rest_framework import serializers
from products.models import Product, ProductImage, ProductSize, ProductColor

class ProductImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['product', 'image', 'caption']

class ProductSizeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['name', 'quantity']

class ProductColorSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['name']

class ProductSerializers(serializers.ModelSerializer):
    productimage_set = ProductImageSerializers(many=True, read_only=True)
    productsize_set = ProductSizeSerializers(many=True)
    productcolor_set = ProductColorSerializers(many=True)

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'description', 'material', 'origin', 'price', 'productimage_set', 'productsize_set', 'productcolor_set']

    def create(self, validated_data):
        productsize_set = validated_data.pop('productsize_set')
        productcolor_set = validated_data.pop('productcolor_set')

        product = Product.objects.create(**validated_data)

        for productsize in productsize_set:
            ProductSize.objects.create(product=product, **productsize)

        for productcolor in productcolor_set:
            ProductColor.objects.create(product=product, **productcolor)

        return product