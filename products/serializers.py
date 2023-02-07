from rest_framework import serializers
from products.models import Product, ProductImage, Review, Brand, Collection
from accounts.serializers import UserBaseSerializer

class ProductImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'caption', 'position']

    def create(self, validated_data):
        product = Product.objects.get(id=self.context['pk'])
        productimage = ProductImage.objects.create(product=product, **validated_data)
        return productimage

class ReviewSerializers(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'title', 'text', 'rating', 'created_at']

class ReviewWriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'text', 'rating', 'created_at']

    def create(self, validated_data):
        product = Product.objects.get(id=self.context['pk'])
        user = self.context['user']
        review = Review.objects.create(product=product, user=user, **validated_data)
        return review

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']

class ProductBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'description', 'category', 'material', 'size', 'color', 'origin', 'brand', 'price', 'quantity']

class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    productimage_set = ProductImageSerializers(many=True, read_only=True)
    review_set = ReviewSerializers(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'description', 'category', 'material', 'size', 'color', 'origin', 'price', 'quantity', 'created_at', 'brand', 'productimage_set', 'review_set']

class ProductBannerImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'caption', 'product']

class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Collection
        fields = ['url', 'id', 'name', 'description', 'products', 'active', 'created_at', 'start_date', 'end_date']