from django.urls import path

from .views import *

# from django.contrib.auth import views as auth_views
# from .forms import CustomAuthenticationForm

urlpatterns = [
    path("register/", register, name="register"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    # path(
    #     "login/",
    #     auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm),
    #     name="login",
    # ),
]
