from rest_framework import views, mixins, viewsets, generics
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from products.models import Product, ProductImage, ProductSize, ProductColor
from products.serializers import ProductSerializers, ProductImageSerializers

class ProductViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = Product.objects.prefetch_related('productimage_set','productsize_set','productcolor_set').all()
    serializer_class = ProductSerializers

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializers
    