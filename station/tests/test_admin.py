from django.test import TestCase
from django.contrib.admin.sites import site

from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Order,
    Ticket,
)

class AdminTests(TestCase):
    """Admin interface tests."""

    def test_station_admin_registered(self):
        """Test Station model registered in admin site."""
        self.assertIn(Station, site._registry)
        admin_class = site._registry.get(Station)
        self.assertEqual(admin_class.list_display, ("name", "latitude", "longitude"))

    def test_route_admin_registered(self):
        """Test Route model registered in admin site."""
        self.assertIn(Route, site._registry)
        admin_class = site._registry.get(Route)
        self.assertEqual(admin_class.list_display, ("source", "destination", "distance"))

    def test_train_admin_registered(self):
        """Test Train model registered in admin site."""
        self.assertIn(Train, site._registry)
        admin_class = site._registry.get(Train)
        expected = ("name", "train_type", "cargo_num", "places_in_cargo", "capacity")
        self.assertEqual(admin_class.list_display, expected)

    def test_crew_admin_readonly_fields(self):
        """Test CrewAdmin has readonly_fields."""
        self.assertIn(Crew, site._registry)
        admin_class = site._registry.get(Crew)
        self.assertIn("full_name", admin_class.readonly_fields)
        self.assertEqual(admin_class.list_display, ("first_name", "last_name", "full_name"))

    def test_journey_admin_configuration(self):
        """Test JourneyAdmin configuration."""
        self.assertIn(Journey, site._registry)
        admin_class = site._registry.get(Journey)
        self.assertEqual(admin_class.list_display, ("route", "train", "departure_time", "arrival_time"))
        self.assertEqual(admin_class.list_filter, ("route", "train"))
        self.assertIn("crew", admin_class.filter_horizontal)

    def test_order_admin_configuration(self):
        """Test OrderAdmin configuration."""
        self.assertIn(Order, site._registry)
        admin_class = site._registry.get(Order)
        self.assertEqual(admin_class.list_display, ("id", "user", "created_at"))
        self.assertEqual(admin_class.list_filter, ("user", "created_at"))

    def test_ticket_admin_configuration(self):
        """Test TicketAdmin configuration."""
        self.assertIn(Ticket, site._registry)
        admin_class = site._registry.get(Ticket)
        self.assertEqual(admin_class.list_display, ("id", "journey", "cargo", "seat", "order"))
        self.assertEqual(admin_class.list_filter, ("journey",))

    def test_all_models_registered(self):
        """Test that all models are registered in the admin site."""
        expected_models = {Station, Route, TrainType, Train, Crew, Journey, Order, Ticket}
        registered_models = set(site._registry.keys())
        self.assertTrue(expected_models.issubset(registered_models))