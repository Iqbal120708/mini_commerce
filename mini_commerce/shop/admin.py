from django.contrib import admin
from unfold.admin import ModelAdmin

from .forms import ProductForm
from .models import Cart, Image, Product


class BaseModelAdmin(ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
class ProductAdmin(BaseModelAdmin):
    form = ProductForm


class CartAdmin(BaseModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Image, BaseModelAdmin)
