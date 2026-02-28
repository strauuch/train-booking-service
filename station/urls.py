from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet, RouteViewSet, TrainTypeViewSet, TrainViewSet, CrewViewSet

app_name = "station"

router = routers.DefaultRouter()

router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("crews", CrewViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
