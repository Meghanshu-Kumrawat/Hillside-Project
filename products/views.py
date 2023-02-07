from rest_framework import views, mixins, viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from functools import reduce
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from products.models import Product, ProductImage, Review, Brand
from products.serializers import (ProductSerializer, ProductBaseSerializer, ProductImageSerializers, ReviewSerializers, 
        ReviewWriteSerializers, 
        ProductBannerImageSerializers, BrandSerializer)

from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, PolymorphicProxySerializer,
    extend_schema_view, extend_schema, inline_serializer, extend_schema_serializer, OpenApiExample
)

@extend_schema(tags=['brand'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a paginated list of brands according to query parameters (10 projects per page)',
        responses={
            '200': BrandSerializer,
        }),
    create=extend_schema(
        summary='Method creates a new brand',
        responses={
            '201': BrandSerializer,
        }),
    retrieve=extend_schema(
        summary='Method returns details of a specific brand',
        responses={
            '200': BrandSerializer,
        }),
    destroy=extend_schema(
        summary='Method deletes a specific brand',
        responses={
            '204': OpenApiResponse(description='The brand has been deleted'),
        }),
    partial_update=extend_schema(
        summary='Methods does a partial update of chosen fields in a brand',
        responses={
            '200': BrandSerializer,
        }),
    update=extend_schema(
        summary='Methods does a update of chosen fields in a brand',
        responses={
            '200': BrandSerializer,
        })
)
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

@extend_schema(tags=['banner images'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a paginated list of banner images according to query parameters (10 projects per page)',
        responses={
            '200': ProductBannerImageSerializers, 
        })
)
class ProductBannerViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = ProductImage.objects.select_related('product').all()
    serializer_class = ProductBannerImageSerializers
    permission_classes = [IsAdminUser, IsAuthenticated]


@extend_schema(tags=['products'])
@extend_schema_view(
    list=extend_schema(
        summary='Returns a paginated list of products according to query parameters (10 projects per page)',
        responses={
            '200': ProductSerializer,
        }),
    create=extend_schema(
        summary='Method creates a new product',
        responses={
            '201': ProductSerializer,
        }),
    retrieve=extend_schema(
        summary='Method returns details of a specific product',
        responses={
            '200': ProductSerializer,
        }),
    destroy=extend_schema(
        summary='Method deletes a specific product',
        responses={
            '204': OpenApiResponse(description='The product has been deleted'),
        }),
    partial_update=extend_schema(
        summary='Methods does a partial update of chosen fields in a product',
        responses={
            '200': ProductSerializer,
        }),
    update=extend_schema(
        summary='Methods does a update of chosen fields in a product',
        responses={
            '200': ProductSerializer,
        })
)
class ProductViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Product.objects.prefetch_related('productimage_set', 'review_set').all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        brand = self.request.query_params.get('brand')
        filters = [Q(category=category) if category else Q(), Q(brand=brand) if brand else Q()]
        queryset = queryset.filter(reduce(lambda x, y: x & y, filters))
        return queryset
        # if category or brand:
        #     queryset = queryset.filter(Q(category=category) and Q(brand=brand))
        # return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ProductSerializer
        return ProductBaseSerializer


    @extend_schema(methods=['GET'],
        summary='Method returns information of the product images for the specific product with the selected id',
        responses={
            '200': ProductImageSerializers(many=True),
        })
    @extend_schema(methods=['POST'],
        summary='Method create/upload the product images for the specific product with the selected id',
        # parameters=[OpenApiParameter('product')],
        request = ProductImageSerializers,
        responses={
            '200': ProductImageSerializers(),
        })
    @extend_schema(methods=['PATCH'],
        summary='Methods does a partial update of chosen fields in a product images for the specific product with the selected id',
        request = ProductImageSerializers,
        responses={
            '200': ProductImageSerializers(),
        })
    @extend_schema(methods=['DELETE'],
        summary='Method delete the product images for the specific product with the selected id',
        request = ProductImageSerializers,
        responses={
            '200': OpenApiResponse(description='Image object with id = {id} deleted.'),
        })
    @action(detail=True, methods=['GET', 'POST', 'PATCH', 'DELETE'], url_path=r'images/?$', serializer_class=ProductImageSerializers)
    def images(self, request, pk, *args):
        """ to modify images of the specific product"""
        self._object = self.get_object() # force to call check_object_permissions
        print(self._object)
        if request.method == 'GET':
            queryset = ProductImage.objects.filter(product_id=pk).order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ProductImageSerializers(page, many=True,
                    context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,
                context={"request": request})
        elif request.method == 'POST':
            serializer = ProductImageSerializers(data=request.data, context={"pk":pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            try:
                image_ins = ProductImage.objects.get(pk=request.data.get('id'))
            except ProductImage.DoesNotExist:
                return Response({'id': 'Not found, Provide valid image id.'})
            
            serializer = ProductImageSerializers(image_ins, data=request.data, partial=True, context={"pk":pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            try:
                image_ins = ProductImage.objects.get(pk=request.data.get('id'))
            except ProductImage.DoesNotExist:
                return Response({'id': 'Not found, Provide valid image id.'})
            image_ins.delete()
            return Response({"message":f"Image object with id = {request.data.get('id')} deleted."}, status=status.HTTP_200_OK)

        return Response(serializer.data)


    @extend_schema(methods=['GET'],
        summary='Method returns information of the product reviews for the specific product with the selected id',
        responses={
            '200': ReviewSerializers(many=True),
        })
    @extend_schema(methods=['POST'],
        summary='Method create the product review for the specific product with the selected id',
        request = ReviewWriteSerializers,
        responses={
            '200': ReviewSerializers(),
        })
    @extend_schema(methods=['PATCH'],
        summary='Methods does a partial update of chosen fields in a product review for the specific product with the selected id',
        request = ReviewWriteSerializers,
        responses={
            '200': ReviewSerializers(),
        })
    @extend_schema(methods=['DELETE'],
        summary='Method delete the product review for the specific product with the selected id',
        request = ReviewSerializers,
        responses={
            '200': OpenApiResponse(description='Image object with id = {id} deleted.'),
        })
    @action(detail=True, methods=['GET', 'POST', 'PATCH', 'DELETE'], serializer_class=ReviewSerializers)
    def reviews(self, request, pk=None, id=None):
        """ to modify sizes of the specific product"""
        self._object = self.get_object() # force to call check_object_permissions
        if request.method == 'GET':
            queryset = Review.objects.filter(product_id=pk).order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ReviewSerializers(page, many=True,
                    context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,
                context={"request": request})
        elif request.method == 'POST':
            request.data['product'] = pk
            request.data['user'] = self.request.user.pk
            serializer = ReviewWriteSerializers(data=request.data, context={"pk":pk, "user":self.request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            request.data['product'] = pk
            request.data['user'] = self.request.user.pk
            try:
                review_ins = Review.objects.get(pk=request.data.get('id'))
            except Review.DoesNotExist:
                return Response({'id': 'Not found, Provide valid review id.'})
            
            serializer = ReviewWriteSerializers(review_ins, data=request.data, partial=True, context={"pk":pk, "user":self.request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            try:
                review_ins = Review.objects.get(pk=request.data.get('id'))
            except Review.DoesNotExist:
                return Response({'id': 'Not found, Provide valid review id.'})
            review_ins.delete()
            return Response({"message":f"Size object with id = {request.data.get('id')} deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.data)
