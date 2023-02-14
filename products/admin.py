from django.contrib import admin
from products.models import Brand, Category, Product, ProductImage, ProductColor, ProductSize, Review, Collection, CollectionImage
from orders.models import Cart
from django.db.models import Sum

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
    list_display = ['name', 'price', 'total_commited', 'get_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ProductImageInline, ProductSizeInline, ProductColorInline]

    def get_quantity(self, obj):
        return obj.quantity

    def total_commited(self, obj):
        return Cart.objects.filter(product=obj, ordered=True).aggregate(s=Sum("quantity"))['s']


    get_quantity.short_description = "Available"
    total_commited.short_description = "Commited"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'title', 'rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']

class CollectionImageInline(admin.TabularInline):
    model = CollectionImage
    extra = 0\

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_total_products', 'created_at', 'start_date', 'end_date', 'active']
    list_filter = ['created_at', 'start_date', 'end_date', 'active']
    search_fields = ['name']
    inlines = [CollectionImageInline]

    def get_total_products(self, obj):
        return obj.products.all().count()

    get_total_products.short_description = "Products"
