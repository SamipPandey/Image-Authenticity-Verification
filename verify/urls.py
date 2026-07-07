from django.urls import path
from . import views

urlpatterns = [
    path("verify/", views.verify_image, name="verify_image"),
    path("health/", views.health_check, name="health_check"),
]
