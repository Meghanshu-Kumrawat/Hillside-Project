from django.db import models
from enum import Enum
from accounts.models import User, Address
from products.models import Product

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.product.price * self.quantity

class DeliveryChoice(str, Enum):
    FASTEST = 'Fastest'
    PERSONALISED = 'Personalised'

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    def __str__(self):
        return self.value

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Cart)
    delivery_type = models.CharField(max_length=20, choices=DeliveryChoice.choices(), default=DeliveryChoice.FASTEST)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    from_time = models.TimeField(blank=True, null=True)
    to_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ordered_at = models.DateTimeField(auto_now=True)
    total = models.IntegerField(default=0)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
