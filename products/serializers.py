from rest_framework import serializers
from products.models import Product, ProductImage, ProductSize, ProductColor

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


class ProductSerializers(serializers.ModelSerializer):
    productimage_set = ProductImageSerializers(many=True, read_only=True)
    productsize_set = ProductSizeSerializers(many=True, read_only=True)
    productcolor_set = ProductColorSerializers(many=True, read_only=True)

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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.material = validated_data.get('material', instance.material)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.price = validated_data.get('price', instance.price)

        return instance