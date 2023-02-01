from rest_framework import views, mixins, viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from functools import reduce

from products.models import Product, ProductImage, ProductSize, ProductColor, Review, Brand
from products.serializers import (ProductSerializer, ProductBaseSerializer, ProductImageSerializers, ProductSizeSerializers, ProductColorSerializers, ReviewSerializers, 
        ProductImageWriteSerializers, ProductColorWriteSerializers, ProductSizeWriteSerializers, ReviewWriteSerializers, 
        ProductBannerImageSerializers, BrandSerializer)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductBannerViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = ProductImage.objects.select_related('product').all()
    serializer_class = ProductBannerImageSerializers

class ProductViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Product.objects.prefetch_related('productimage_set','productsize_set','productcolor_set', 'review_set').all()
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
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            return ProductSerializer
        return ProductBaseSerializer

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
            serializer = ProductImageWriteSerializers(data=request.data, context={"pk":pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            try:
                image_ins = ProductImage.objects.get(pk=request.data.get('id'))
            except ProductImage.DoesNotExist:
                return Response({'id': 'Not found, Provide valid image id.'})
            
            serializer = ProductImageWriteSerializers(image_ins, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            try:
                image_ins = ProductImage.objects.get(pk=request.data.get('id'))
            except ProductImage.DoesNotExist:
                return Response({'id': 'Not found, Provide valid image id.'})
            image_ins.delete()
            return Response({"message":f"Image object with id = {request.data.get('id')} deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.data)

    @action(detail=True, methods=['GET', 'POST', 'PATCH', 'DELETE'], url_path=r'colors/?$', serializer_class=ProductColorSerializers)
    def colors(self, request, pk, *args):
        """ to modify colors of the specific product"""
        self._object = self.get_object() # force to call check_object_permissions
        print(self._object)
        if request.method == 'GET':
            queryset = ProductColor.objects.filter(product_id=pk).order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ProductColorSerializers(page, many=True,
                    context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,
                context={"request": request})
        elif request.method == 'POST':
            request.data['product'] = pk
            serializer = ProductColorWriteSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            request.data['product'] = pk
            try:
                color_ins = ProductColor.objects.get(pk=request.data.get('id'))
            except ProductColor.DoesNotExist:
                return Response({'id': 'Not found, Provide valid color id.'})
            
            serializer = ProductColorWriteSerializers(color_ins, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            try:
                color_ins = ProductColor.objects.get(pk=request.data.get('id'))
            except ProductColor.DoesNotExist:
                return Response({'id': 'Not found, Provide valid color id.'})
            color_ins.delete()
            return Response({"message":f"Color object with id = {request.data.get('id')} deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.data)

    @action(detail=True, methods=['GET', 'POST', 'PATCH', 'DELETE'], url_path=r'sizes/?$', serializer_class=ProductSizeSerializers)
    def sizes(self, request, pk, *args):
        """ to modify sizes of the specific product"""
        self._object = self.get_object() # force to call check_object_permissions
        print(self._object)
        if request.method == 'GET':
            queryset = ProductSize.objects.filter(product_id=pk).order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ProductSizeSerializers(page, many=True,
                    context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,
                context={"request": request})
        elif request.method == 'POST':
            request.data['product'] = pk
            serializer = ProductSizeWriteSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            request.data['product'] = pk
            try:
                size_ins = ProductSize.objects.get(pk=request.data.get('id'))
            except ProductSize.DoesNotExist:
                return Response({'id': 'Not found, Provide valid size id.'})
            
            serializer = ProductSizeWriteSerializers(size_ins, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            try:
                size_ins = ProductSize.objects.get(pk=request.data.get('id'))
            except ProductSize.DoesNotExist:
                return Response({'id': 'Not found, Provide valid size id.'})
            size_ins.delete()
            return Response({"message":f"Size object with id = {request.data.get('id')} deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.data)
 
    @action(detail=True, methods=['GET', 'POST', 'PATCH', 'DELETE'], serializer_class=ReviewSerializers)
    def reviews(self, request, pk=None, id=None):
        """ to modify sizes of the specific product"""
        self._object = self.get_object() # force to call check_object_permissions
        if request.method == 'GET':
            queryset = Review.objects.filter(product_id=pk).order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True,
                    context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True,
                context={"request": request})
        elif request.method == 'POST':
            request.data['product'] = pk
            request.data['user'] = self.request.user.pk
            serializer = ReviewWriteSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'PATCH':
            request.data['product'] = pk
            request.data['user'] = self.request.user.pk
            try:
                review_ins = Review.objects.get(pk=request.data.get('id'))
            except Review.DoesNotExist:
                return Response({'id': 'Not found, Provide valid review id.'})
            
            serializer = ReviewWriteSerializers(review_ins, data=request.data, partial=True)
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
