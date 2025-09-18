import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_at:
            self.created_at = now()
        self.updated_at = now()

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Image(BaseModel):
    path = models.CharField(max_length=255)

    def __str__(self):
        return os.path.basename(self.path)


class Product(BaseModel):
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Cart(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # quantity = models.IntegerField(default=1)

    def clean(self):
        errors = {}

        # stok habis
        if self.product.stock <= 0:
            errors["product"] = f"Produk '{self.product.name}' ini sudah habis stoknya."

        # jumlah dipesan lebih besar dari stok
        # if self.quantity > self.product.quantity:
        #     errors['quantity'] = f"Stok hanya tersedia {self.product.quantity}."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name}"
