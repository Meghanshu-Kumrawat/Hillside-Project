from django.contrib import admin
from products.models import Brand, Category, Product, ProductImage, ProductColor, ProductSize, Review, Collection


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 0

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ProductImageInline, ProductSizeInline, ProductColorInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'title', 'rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'start_date', 'end_date', 'active']
    list_filter = ['created_at', 'start_date', 'end_date', 'active']
    search_fields = ['name']