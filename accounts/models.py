from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=500, blank=True, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.username)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=10)
    full_address = models.TextField()

    def __str__(self):
        return str(self.user.username)