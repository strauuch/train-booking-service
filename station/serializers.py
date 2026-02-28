from django.db import transaction
from rest_framework import serializers
from .models import Station, Route, TrainType, Train, Crew, Journey, Ticket, Order


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        journey = attrs.get("journey")
        cargo = attrs.get("cargo")
        seat = attrs.get("seat")

        if not journey:
            raise serializers.ValidationError({"journey": "Journey is required"})

        train = journey.train

        Ticket.validate_ticket(
            cargo,
            seat,
            train.cargo_num,
            train.places_in_cargo,
            serializers.ValidationError,
        )

        return attrs

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            journey_ids = {t["journey"].id for t in tickets_data}
            Journey.objects.select_for_update().filter(id__in=journey_ids).exists()

            for ticket_data in tickets_data:
                if Ticket.objects.filter(
                    journey=ticket_data["journey"],
                    cargo=ticket_data["cargo"],
                    seat=ticket_data["seat"],
                ).exists():
                    raise serializers.ValidationError(
                        f"Seat {ticket_data['seat']} in cargo {ticket_data['cargo']} is already taken."
                    )

                Ticket.objects.create(order=order, **ticket_data)
            return order
