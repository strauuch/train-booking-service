from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Station, Route, TrainType, Train, Crew, Journey
from .serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    CrewSerializer,
    JourneySerializer,
    JourneyListSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return Route.objects.select_related("source", "destination")
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return Train.objects.select_related("train_type")
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("route", "train")

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related(
                "route__source", "route__destination", "train__train_type"
            ).prefetch_related("crew")
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return JourneyListSerializer
        return JourneySerializer
