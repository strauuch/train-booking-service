from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Ticket,
    Order,
)

User = get_user_model()


class ModelTests(TestCase):
    """Tests for station application models."""

    def setUp(self):
        """Set up initial data for tests."""
        self.user = User.objects.create_user(
            email="test@test.com",
            password="password"
        )

        self.station1 = Station.objects.create(
            name="Station A",
            latitude=10.0,
            longitude=10.0
        )

        self.station2 = Station.objects.create(
            name="Station B",
            latitude=20.0,
            longitude=20.0
        )

        self.train_type = TrainType.objects.create(name="Express")

        self.train = Train.objects.create(
            name="Polar",
            cargo_num=2,
            places_in_cargo=10,
            train_type=self.train_type
        )

        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe"
        )

        self.route = Route.objects.create(
            source=self.station1,
            destination=self.station2,
            distance=100
        )

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2)
        )

        self.order = Order.objects.create(user=self.user)

    def test_station_str(self):
        """Test Station string representation."""
        self.assertEqual(str(self.station1), "Station A")

    def test_route_str(self):
        """Test Route string representation."""
        self.assertEqual(str(self.route), "Station A - Station B")

    def test_train_capacity_property(self):
        """Test Train capacity property calculation."""
        self.assertEqual(self.train.capacity, 20)

    def test_crew_full_name_property(self):
        """Test Crew full_name property."""
        self.assertEqual(self.crew.full_name, "John Doe")

    def test_train_min_value_validation(self):
        """Test that train cargo_num cannot be less than 1."""
        train = Train(
            name="Invalid",
            cargo_num=0,
            places_in_cargo=10,
            train_type=self.train_type
        )
        with self.assertRaises(ValidationError):
            train.full_clean()

    def test_journey_clean_validation(self):
        """Test that arrival must be after departure."""
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() - timedelta(hours=1)
        )
        with self.assertRaises(ValidationError):
            journey.full_clean()

    def test_journey_m2m_crew_assignment(self):
        """Test ManyToMany crew assignment to Journey."""
        self.journey.crew.add(self.crew)
        self.assertEqual(self.journey.crew.count(), 1)
        self.assertIn(self.crew, self.journey.crew.all())

    def test_route_unique_constraint(self):
        """Test Route source-destination uniqueness."""
        with self.assertRaises(IntegrityError):
            Route.objects.create(
                source=self.station1,
                destination=self.station2,
                distance=200
            )

    def test_ticket_validation_range_error(self):
        """Test Ticket seat/cargo range validation."""
        ticket = Ticket(
            journey=self.journey,
            order=self.order,
            cargo=3,   # invalid (max 2)
            seat=1
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_unique_constraint_db(self):
        """Database unique constraint validation via full_clean."""
        Ticket.objects.create(
            journey=self.journey,
            order=self.order,
            cargo=1,
            seat=1
        )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                journey=self.journey,
                order=self.order,
                cargo=1,
                seat=1
            )