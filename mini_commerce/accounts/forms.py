from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth.models import User
# from django import forms
# from django.contrib.auth.forms import AuthenticationForm
# from django.utils.translation import gettext_lazy as _


# class CustomAuthenticationForm(AuthenticationForm):
#     def confirm_login_allowed(self, user):
#         if not user.is_active:
#             raise forms.ValidationError(
#                 _("Akun Anda belum aktif. Silakan cek email untuk aktivasi."),
#                 code="inactive",
#             )


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]
        # labels = {
        #     "password1": "Password",
        #     "password2": "Password Confirm",
        # }
