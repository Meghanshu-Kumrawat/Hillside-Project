from django.contrib import admin
from orders.models import Cart, Order, Payment



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'ordered_at', 'received', 'payment_status', 'delivery_method']
    list_filter = ['created_at']

    def payment_status(self, obj):
        return "Payment done" if obj.payment else "Payment pending"

    def delivery_method(self, obj):
        return obj.delivery_type

# admin.site.register(Cart)
# admin.site.register(Payment)
