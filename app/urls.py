from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("", login_required(views.index), name="genvariant_index"),
    path(
        "variant/<str:variant_id>/",
        login_required(views.variant_detail),
        name="variant_detail",
    ),
    path("documentation/", login_required(views.documentation), name="documentation"),
    path("about/", login_required(views.about), name="about"),
    path("profile/", login_required(views.profile), name="profile"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("samples/", login_required(views.sample_list), name="sample_list"),
    path(
        "samples/<str:sample_name>/",
        login_required(views.sample_detail),
        name="sample_detail",
    ),
]
