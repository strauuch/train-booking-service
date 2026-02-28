from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet, RouteViewSet

app_name = "station"

router = routers.DefaultRouter()

router.register("stations", StationViewSet)
router.register("routers", RouteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
