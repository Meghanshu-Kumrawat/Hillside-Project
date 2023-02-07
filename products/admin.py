from django.contrib import admin
from products.models import Brand, Product, ProductImage, Review


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ProductImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'title', 'rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']