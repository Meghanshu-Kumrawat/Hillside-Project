from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    

    def __str__(self):
        return self.username