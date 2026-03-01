from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from station.models import Station, Route, TrainType, Train, Crew, Journey, Ticket, Order
from station.serializers import (
    StationSerializer, RouteSerializer, RouteListSerializer,
    TrainTypeSerializer, TrainSerializer, TrainListSerializer,
    CrewSerializer, JourneySerializer, JourneyListSerializer,
    TicketSerializer, TicketRetrieveSerializer, OrderSerializer,
)
from user.models import User


class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password")
        self.station1 = Station.objects.create(name="A", latitude=10.0, longitude=10.0)
        self.station2 = Station.objects.create(name="B", latitude=20.0, longitude=20.0)
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(name="Polar", cargo_num=2, places_in_cargo=10, train_type=self.train_type)
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.route = Route.objects.create(source=self.station1, destination=self.station2, distance=100)

        self.journey = Journey.objects.create(
            route=self.route, train=self.train,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2)
        )
        self.journey.crew.add(self.crew)

        self.past_journey = Journey.objects.create(
            route=self.route, train=self.train,
            departure_time=timezone.now() - timedelta(days=2),
            arrival_time=timezone.now() - timedelta(days=1)
        )

    def test_station_serializer_fields(self):
        """Validate StationSerializer contains the correct fields."""
        serializer = StationSerializer(self.station1)
        self.assertEqual(set(serializer.data.keys()), {"id", "name", "latitude", "longitude"})

    def test_route_serializer_fields(self):
        """Validate RouteSerializer basic fields."""
        serializer = RouteSerializer(self.route)
        self.assertEqual(set(serializer.data.keys()), {"id", "source", "destination", "distance"})

    def test_route_list_serializer_nested_representation(self):
        """Validate RouteListSerializer correctly nests StationSerializer."""
        serializer = RouteListSerializer(self.route)
        self.assertIsInstance(serializer.data["source"], dict)
        self.assertEqual(serializer.data["source"]["name"], "A")

    def test_train_type_serializer_fields(self):
        """Validate TrainTypeSerializer fields."""
        serializer = TrainTypeSerializer(self.train_type)
        self.assertEqual(set(serializer.data.keys()), {"id", "name"})

    def test_train_serializer_fields(self):
        """Validate TrainSerializer fields."""
        serializer = TrainSerializer(self.train)
        self.assertEqual(set(serializer.data.keys()), {"id", "name", "cargo_num", "places_in_cargo", "train_type", "capacity"})

    def test_train_serializer_capacity_readonly(self):
        """Ensure capacity field is read-only and reflects the calculation."""
        serializer = TrainSerializer(self.train)
        self.assertEqual(serializer.data["capacity"], 20)

    def test_train_list_serializer_train_type_slug_representation(self):
        """Validate TrainListSerializer uses slug for train_type."""
        serializer = TrainListSerializer(self.train)
        self.assertEqual(serializer.data["train_type"], "Express")

    def test_crew_serializer_fields(self):
        """Validate CrewSerializer fields."""
        serializer = CrewSerializer(self.crew)
        self.assertEqual(set(serializer.data.keys()), {"id", "first_name", "last_name", "full_name"})

    def test_crew_serializer_full_name_readonly(self):
        """Ensure full_name is read-only."""
        serializer = CrewSerializer(self.crew)
        self.assertEqual(serializer.data["full_name"], "John Doe")

    def test_journey_serializer_fields(self):
        """Validate JourneySerializer fields."""
        serializer = JourneySerializer(self.journey)
        self.assertEqual(set(serializer.data.keys()), {"id", "route", "train", "departure_time", "arrival_time", "crew"})

    def test_journey_serializer_validation_arrival_time(self):
        """Ensure validation fails if arrival_time is not after departure_time."""
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() - timedelta(hours=1),
            "crew": [self.crew.id],
        }
        serializer = JourneySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("arrival_time", serializer.errors)

    def test_journey_list_serializer_nested_structure(self):
        """Validate nested representation in JourneyListSerializer."""
        serializer = JourneyListSerializer(self.journey)
        self.assertIsInstance(serializer.data["route"], dict)
        self.assertIsInstance(serializer.data["train"], dict)
        self.assertIsInstance(serializer.data["crew"], list)

    def test_ticket_serializer_fields(self):
        """Validate TicketSerializer fields."""
        ticket = Ticket.objects.create(journey=self.journey, cargo=1, seat=1, order=Order.objects.create(user=self.user))
        serializer = TicketSerializer(ticket)
        self.assertEqual(set(serializer.data.keys()), {"id", "cargo", "seat", "journey"})

    def test_ticket_serializer_journey_required(self):
        """Ensure validation fails if journey field is missing."""
        data = {"cargo": 1, "seat": 1}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("journey", serializer.errors)

    def test_ticket_serializer_journey_validation_past_date(self):
        """Ensure booking tickets for a past journey raises a ValidationError."""
        data = {"journey": self.past_journey.id, "cargo": 1, "seat": 1}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("journey", serializer.errors)

    def test_ticket_serializer_seat_cargo_range_validation(self):
        """Ensure validation fails if cargo or seat number exceeds capacity."""
        data = {"journey": self.journey.id, "cargo": 3, "seat": 11}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cargo", serializer.errors)
        self.assertIn("seat", serializer.errors)

    def test_ticket_retrieve_serializer_nested_representation(self):
        """Validate TicketRetrieveSerializer nests full JourneyListSerializer data."""
        ticket = Ticket.objects.create(journey=self.journey, cargo=1, seat=1, order=Order.objects.create(user=self.user))
        serializer = TicketRetrieveSerializer(ticket)
        self.assertIsInstance(serializer.data["journey"], dict)
        self.assertIn("route", serializer.data["journey"])

    def test_order_serializer_fields(self):
        """Validate OrderSerializer fields including read-only tickets_count."""
        Order.objects.create(user=self.user)
        order = Order.objects.annotate(tickets_count=Count("tickets")).get(user=self.user)
        serializer = OrderSerializer(order)
        expected_fields = {"id", "tickets", "created_at", "tickets_count"}
        self.assertTrue(expected_fields.issubset(serializer.data.keys()))

    def test_order_serializer_tickets_count_is_readonly(self):
        """Ensure tickets_count is read-only and not accepted in input."""
        data = {"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}], "tickets_count": 99}
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save(user=self.user)
        self.assertEqual(order.tickets.count(), 1)

    def test_order_serializer_ticket_duplicate_validation(self):
        """Ensure duplicate seat/cargo numbers for the same journey raise ValidationError during save."""
        data = {
            "tickets": [
                {"journey": self.journey.id, "cargo": 1, "seat": 1},
                {"journey": self.journey.id, "cargo": 1, "seat": 1}
            ]
        }
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as cm:
            serializer.save(user=self.user)
        self.assertIn("Duplicate seat", str(cm.exception))

    def test_order_serializer_atomic_creation_with_select_for_update(self):
        """Verify atomic creation and that select_for_update is triggered."""
        data = {"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}]}
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        with patch("station.models.Journey.objects.select_for_update") as mocked_sfu:
            mocked_sfu.return_value.filter.return_value = [self.journey]
            serializer.save(user=self.user)
            self.assertTrue(mocked_sfu.called)

    def test_order_serializer_integrity_error_on_taken_seat(self):
        """Verify that taken seats raise ValidationError."""
        Ticket.objects.create(
            journey=self.journey, cargo=1, seat=1,
            order=Order.objects.create(user=self.user)
        )
        data = {"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}]}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tickets", serializer.errors)
        ticket_errors = serializer.errors["tickets"][0]
        self.assertIn("non_field_errors", ticket_errors)
        self.assertIn("unique", str(ticket_errors["non_field_errors"]))

    def test_order_serializer_empty_tickets_validation(self):
        """Ensure an Order cannot be created with an empty tickets list."""
        data = {"tickets": []}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tickets", serializer.errors)