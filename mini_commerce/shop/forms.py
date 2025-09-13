from django import forms
from django.conf import settings
from .models import Product, Image, Cart
from django.core.files.storage import FileSystemStorage
import os
import uuid
from django.utils.safestring import mark_safe

class ProductForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = ["name", "desc", "price", "stock", "image_file"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.image:
            file_url = os.path.join(settings.MEDIA_URL, self.instance.image.path)

            file_url = os.path.join(settings.MEDIA_URL, self.instance.image.path)
            self.fields['image_file'].help_text = mark_safe(
                f'<span style="font-weight:bold;">Current file:</span> {self.instance.image}<br>'
                f'<a href="{file_url}" target="_blank" style="color:purple; text-decoration:underline;">View current image</a>'
            )
            
            self.fields['image_file'].widget.attrs.update({'accept':'image/*'})

    def save(self, commit=True):
        product = super().save(commit=False)
        image_file = self.cleaned_data.get("image_file")

        if image_file:
            # buat folder unik
            folder_path = os.path.join(settings.MEDIA_ROOT, "uploads", str(uuid.uuid4()))
            fs = FileSystemStorage(location=folder_path)
        
            # nama file aman
            from django.utils.text import get_valid_filename
            filename = get_valid_filename(image_file.name)
        
            # simpan file di folder unik
            file_path = fs.save(filename, image_file)
        
            # path relatif untuk simpan ke DB
            rel_path = os.path.join("uploads", os.path.basename(folder_path), file_path)
            image = Image.objects.create(path=rel_path)
            product.image = image
        

        if commit:
            product.save()
        return product
        