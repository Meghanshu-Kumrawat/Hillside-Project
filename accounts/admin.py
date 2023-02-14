from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import User, Address
from rest_framework.authtoken.models import TokenProxy
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from orders.models import Order
from django.db.models import Sum

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_active', 'email', 'phone', 'address', 'orders', 'amount_spent']
    list_filter = ['date_of_birth', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'phone']
    inlines = [AddressInline]

    def address(self, obj):
        address = Address.objects.filter(user=obj).first()
        return address.full_address if address else "-"

    def orders(self, obj):
        return Order.objects.filter(user=obj).count()

    def amount_spent(self, obj):
        return Order.objects.filter(user=obj, ordered=True).aggregate(s=Sum("total"))['s']


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

admin.site.unregister(SocialToken)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
