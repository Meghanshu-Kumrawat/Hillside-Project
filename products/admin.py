from django.contrib import admin
from products.models import Brand, Product, ProductColor, ProductImage, ProductSize, Review


admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductColor)
admin.site.register(ProductSize)
admin.site.register(ProductImage)
admin.site.register(Review)