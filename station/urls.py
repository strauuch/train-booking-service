from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet, RouteViewSet, TrainTypeViewSet

app_name = "station"

router = routers.DefaultRouter()

router.register("stations", StationViewSet)
router.register("routers", RouteViewSet)
router.register("train-types", TrainTypeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
