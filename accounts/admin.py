from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import User, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'date_of_birth']
    list_filter = ['date_of_birth', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'phone']
    inlines = [AddressInline]


admin.site.unregister(Group)
