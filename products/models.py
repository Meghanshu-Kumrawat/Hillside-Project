from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from enum import Enum
from accounts.models import User


class CategoryChoice(str, Enum):
    TOPS = 'Tops / outer'
    BOTTOMS = 'Bottoms'
    ONE_PIECE = 'One piece / Tunic'
    ACCESSORIES = 'Accessories'
    OTHERS = 'Others'

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    def __str__(self):
        return self.value

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    material = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CategoryChoice.choices(),
                              default=CategoryChoice.OTHERS)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    caption = models.CharField(max_length=255, blank=True)

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

