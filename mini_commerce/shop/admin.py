from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Product, Cart
from .forms import ProductForm

class BaseModelAdmin(ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
        
# Register your models here.
class ProductAdmin(BaseModelAdmin):
    form = ProductForm
    
admin.site.register(Cart)
class CartAdmin(BaseModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)