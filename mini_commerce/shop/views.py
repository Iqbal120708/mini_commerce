from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

def product_list(request):
    products = Product.objects.all().order_by("-created_at")
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Logic pagination range
    current = page_obj.number
    total = paginator.num_pages

    if total <= 5:
        page_range = range(1, total + 1)
    else:
        # jika total = 8
        # jika current 1/2/3
        if current <= 3: # hasil  [1, 2, 3, "...", total]
            page_range = [1, 2, 3, "...", total]
        # jika current = 6/7/8
        elif current >= total - 2: # hasil [1, "...", 6, 7, 8]
            page_range = [1, "...", total-2, total-1, total]
        # jika current = 4
        else: # hasil [1, "...", 3, 4, 5, "...", 8]
            page_range = [1, "...", current-1, current, current+1, "...", total]

    return render(request, "shop/product_list.html", {
        "page_obj": page_obj,
        "page_range": page_range,
        "MEDIA_URL": settings.MEDIA_URL
    })

@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        if not product_id:
            messages.error(request, "Produk tidak valid.")
            return redirect("product_list")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Produk tidak ditemukan.")
            return redirect("product_list")
            
        carts = Cart.objects.filter(user=request.user)
        if carts.count() >= 10:
            messages.error(
                request,
                "Keranjang Anda sudah mencapai batas maksimum 10 produk. "
                "Hapus beberapa item sebelum menambahkan produk baru."
            )
            return redirect("product_list")

        try:
            cart, created = Cart.objects.get_or_create(product=product, user=request.user)
        except ValidationError as e:
            for message in e.messages:
                messages.error(request, message)
            return redirect("product_list")

        if not created:
            messages.info(request, "Produk sudah ada di keranjang.")
        else:
            messages.success(request, "Produk berhasil ditambahkan ke keranjang!")

    return redirect("product_list")

@login_required
def cart_list(request):
    cart_list = Cart.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "shop/cart_list.html", {
        "cart_list": cart_list,
        "MEDIA_URL": settings.MEDIA_URL
    })
