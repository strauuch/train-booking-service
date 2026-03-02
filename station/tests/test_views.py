from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from station.models import *

User = get_user_model()


class UltimateViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin@test.com", "pass")
        self.user = User.objects.create_user("user@test.com", "pass")
        self.stranger = User.objects.create_user("stranger@test.com", "pass")
        self.s1 = Station.objects.create(name="A", latitude=0, longitude=0)
        self.s2 = Station.objects.create(name="B", latitude=1, longitude=1)
        self.tt = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="T", cargo_num=1, places_in_cargo=10, train_type=self.tt
        )
        self.route = Route.objects.create(
            source=self.s1, destination=self.s2, distance=100
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2026-03-05 10:00:00",
            arrival_time="2026-03-05 12:00:00",
        )

    def _get_data(self, response):
        return response.data.get("results", response.data)

    # --- FILTERING & PAGINATION ---
    def test_journey_filtering_and_pagination(self):
        """Verify filtering by train/route and standard pagination response."""
        self.client.force_authenticate(self.user)
        # Filter by train
        res = self.client.get(reverse("station:journey-list"), {"train": self.train.id})
        self.assertEqual(len(self._get_data(res)), 1)

        # Check pagination structure
        res_paginated = self.client.get(reverse("station:journey-list"), {"page": 1})
        self.assertIn("results", res_paginated.data)

    # --- SERIALIZER SWITCHING (List vs Retrieve) ---
    def test_route_and_journey_serializer_switching(self):
        """Verify that retrieve uses different/nested serializers."""
        self.client.force_authenticate(self.user)
        # Check Route
        res_route = self.client.get(
            reverse("station:route-detail", kwargs={"pk": self.route.id})
        )
        self.assertIsInstance(res_route.data["source"], dict)  # Should be nested dict

        # Check Journey
        res_journey = self.client.get(
            reverse("station:journey-detail", kwargs={"pk": self.journey.id})
        )
        self.assertIsInstance(res_journey.data["route"], dict)

    # --- PERMISSIONS (Forbidden & Isolation) ---
    def test_forbidden_actions(self):
        """Verify strict permission adherence."""
        self.client.force_authenticate(self.user)
        # Train create
        self.assertEqual(
            self.client.post(reverse("station:train-list"), {"name": "T"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Order retrieve forbidden for stranger
        order = Order.objects.create(user=self.user)
        self.client.force_authenticate(self.stranger)
        self.assertEqual(
            self.client.get(
                reverse("station:order-detail", kwargs={"pk": order.id})
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # --- OPTIMIZATION ---
    def test_queryset_optimizations(self):
        """Verify that multiple objects don't trigger N+1 queries."""
        self.client.force_authenticate(self.user)

        for i in range(5):
            station_new = Station.objects.create(
                name=f"Station_{i}", latitude=i, longitude=i
            )
            Route.objects.create(
                source=self.s1, destination=station_new, distance=100 + i
            )

        with self.assertNumQueries(2):
            self.client.get(reverse("station:route-list"))

    # --- ISOLATION ---
    def test_ticket_list_isolation(self):
        """Verify user sees only their tickets in list view."""
        order_user = Order.objects.create(user=self.user)
        order_stranger = Order.objects.create(user=self.stranger)
        Ticket.objects.create(order=order_user, journey=self.journey, cargo=1, seat=1)
        Ticket.objects.create(
            order=order_stranger, journey=self.journey, cargo=1, seat=2
        )

        self.client.force_authenticate(self.user)
        res = self.client.get(reverse("station:ticket-list"))
        self.assertEqual(len(self._get_data(res)), 1)
