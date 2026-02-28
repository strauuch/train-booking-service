from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import IsAdminOrIfAuthenticatedReadOnly, IsOwner

from .models import Station, Route, TrainType, Train, Crew, Journey, Ticket, Order
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
    TicketSerializer,
    OrderSerializer,
    TicketRetrieveSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
    permission_classes = (IsAdminUser,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = (IsAdminUser,)

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
    permission_classes = (IsAdminUser,)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("route", "train")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("journey__train", "journey__route")
    serializer_class = TicketSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )

    def get_queryset(self):
        return Ticket.objects.filter(order__user=self.request.user).select_related(
            "journey__train",
            "journey__route",
        )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TicketRetrieveSerializer
        return TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__train", "tickets__journey__route"
    )
    serializer_class = OrderSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__journey__train", "tickets__journey__route"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
