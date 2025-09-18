from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import CustomUserCreationForm

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # buat token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = f"http://{domain}/accounts/activate/{uid}/{token}/"

            # kirim email
            send_mail(
                "Aktivasi Akun",
                f"Klik link berikut untuk aktivasi akun: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            # messages.success(request, "Registrasi berhasil! Cek email untuk aktivasi.")
            # return redirect("login")
            return render(request, "registration/email_confirmation_message.html")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):

        user.is_active = True
        user.save()
        messages.success(request, "Akun berhasil diaktivasi! Silakan login.")
        return redirect("login")
    else:
        messages.error(request, "Link aktivasi tidak valid atau sudah kadaluarsa.")
        return redirect("register")
