from django.db.models import Count
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)
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
    TicketListSerializer,
    OrderListSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List all stations"),
    create=extend_schema(summary="Create a new station (Admin only)"),
    retrieve=extend_schema(summary="Get station details"),
    update=extend_schema(summary="Update station (Admin only)"),
    partial_update=extend_schema(summary="Partially update station (Admin only)"),
    destroy=extend_schema(summary="Delete station (Admin only)"),
)
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


@extend_schema_view(
    list=extend_schema(summary="List all routes"),
    create=extend_schema(summary="Create a new route (Admin only)"),
    retrieve=extend_schema(summary="Get route details"),
    update=extend_schema(summary="Update route (Admin only)"),
    partial_update=extend_schema(summary="Partially update route (Admin only)"),
    destroy=extend_schema(summary="Delete route (Admin only)"),
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Route.objects.all()
        if self.action in ("list", "retrieve"):
            return Route.objects.select_related("source", "destination")
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return RouteSerializer


@extend_schema_view(
    list=extend_schema(summary="List all train types"),
    create=extend_schema(summary="Create a new train type (Admin only)"),
    retrieve=extend_schema(summary="Get train type details"),
    update=extend_schema(summary="Update train type (Admin only)"),
    partial_update=extend_schema(summary="Partially update train type (Admin only)"),
    destroy=extend_schema(summary="Delete train type (Admin only)"),
)
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminUser,)


@extend_schema_view(
    list=extend_schema(summary="List all trains"),
    create=extend_schema(summary="Create a new train (Admin only)"),
    retrieve=extend_schema(summary="Get train details"),
    update=extend_schema(summary="Update train (Admin only)"),
    partial_update=extend_schema(summary="Partially update train (Admin only)"),
    destroy=extend_schema(summary="Delete train (Admin only)"),
)
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


@extend_schema_view(
    list=extend_schema(summary="List all crew members"),
    create=extend_schema(summary="Create a new crew member (Admin only)"),
    retrieve=extend_schema(summary="Get crew member details"),
    update=extend_schema(summary="Update crew member (Admin only)"),
    partial_update=extend_schema(summary="Partially update crew member (Admin only)"),
    destroy=extend_schema(summary="Delete crew member (Admin only)"),
)
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


@extend_schema_view(
    list=extend_schema(
        summary="List journeys",
        parameters=[
            OpenApiParameter(
                "route", OpenApiTypes.INT, description="Filter by route ID"
            ),
            OpenApiParameter(
                "train", OpenApiTypes.INT, description="Filter by train ID"
            ),
        ],
    ),
    create=extend_schema(summary="Create a new journey (Admin only)"),
    retrieve=extend_schema(summary="Get journey details"),
    update=extend_schema(summary="Update journey (Admin only)"),
    partial_update=extend_schema(summary="Partially update journey (Admin only)"),
    destroy=extend_schema(summary="Delete journey (Admin only)"),
)
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


@extend_schema_view(
    list=extend_schema(summary="List user's own tickets"),
    create=extend_schema(summary="Create a ticket"),
    retrieve=extend_schema(summary="Get ticket details"),
    update=extend_schema(summary="Update ticket"),
    partial_update=extend_schema(summary="Partially update ticket"),
    destroy=extend_schema(summary="Delete ticket"),
)
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
            return TicketListSerializer
        return TicketSerializer


@extend_schema_view(
    list=extend_schema(summary="List user's own orders"),
    create=extend_schema(summary="Create a new order"),
    retrieve=extend_schema(summary="Get order details"),
    update=extend_schema(summary="Update order"),
    partial_update=extend_schema(summary="Partially update order"),
    destroy=extend_schema(summary="Delete order"),
)
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
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("tickets__journey__train", "tickets__journey__route")
            .annotate(tickets_count=Count("tickets"))
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderSerializer