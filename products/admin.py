from django.contrib import admin
from products.models import Brand, Product, ProductImage, Review


admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Review)