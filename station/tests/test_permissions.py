from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from station.permissions import (
    IsAdminOrIfAuthenticatedReadOnly,
    IsOwner,
)

User = get_user_model()


class PermissionTests(TestCase):
    """Tests for custom DRF permissions."""

    def setUp(self):
        """Set up test users and request factory."""
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password",
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            email="user@test.com",
            password="password",
            is_staff=False
        )

        self.permission_admin_readonly = IsAdminOrIfAuthenticatedReadOnly()
        self.permission_owner = IsOwner()

    # ---------------------------------------------------
    # IsAdminOrIfAuthenticatedReadOnly tests
    # ---------------------------------------------------

    def test_admin_can_access_any_method(self):
        """Test admin user can use unsafe methods."""

        request = self.factory.post("/")
        request.user = self.admin_user

        self.assertTrue(
            self.permission_admin_readonly.has_permission(
                request,
                view=None
            )
        )

    def test_authenticated_user_read_only(self):
        """Test authenticated non-admin user can use safe methods."""

        request = self.factory.get("/")
        request.user = self.regular_user

        self.assertTrue(
            self.permission_admin_readonly.has_permission(
                request,
                view=None
            )
        )

    def test_unauthorized_user_safe_methods(self):
        """Test anonymous user can use safe methods."""

        request = self.factory.get("/")
        request.user = None

        self.assertTrue(
            self.permission_admin_readonly.has_permission(
                request,
                view=None
            )
        )

    def test_regular_user_cannot_use_unsafe_methods(self):
        """Test regular user cannot use unsafe methods."""

        request = self.factory.post("/")
        request.user = self.regular_user

        self.assertFalse(
            self.permission_admin_readonly.has_permission(
                request,
                view=None
            )
        )

    # ---------------------------------------------------
    # IsOwner permission tests
    # ---------------------------------------------------

    class MockObject:
        """Mock object for ownership testing."""

        def __init__(self, user=None, order=None):
            self.user = user
            self.order = order

    def test_owner_permission_by_user_field(self):
        """Test owner permission when object has user field."""

        obj = self.MockObject(user=None)

        request = self.factory.get("/")
        request.user = self.regular_user

        obj.user = self.regular_user

        self.assertTrue(
            self.permission_owner.has_object_permission(
                request,
                view=None,
                obj=obj
            )
        )

    def test_owner_permission_by_order_field(self):
        """Test owner permission when object has order field."""

        owner_user = self.regular_user

        class MockOrder:
            def __init__(self, user):
                self.user = user

        class MockObj:
            def __init__(self, order):
                self.order = order

        mock_obj = MockObj(
            order=MockOrder(user=owner_user)
        )

        request = self.factory.get("/")
        request.user = owner_user

        self.assertTrue(
            self.permission_owner.has_object_permission(
                request,
                view=None,
                obj=mock_obj
            )
        )

    def test_owner_permission_denied(self):
        """Test permission denial for non-owner."""

        other_user = User.objects.create_user(
            email="other@test.com",
            password="password"
        )

        class MockObj:
            def __init__(self, user):
                self.user = user

        obj = MockObj(user=other_user)

        request = self.factory.get("/")
        request.user = self.regular_user

        self.assertFalse(
            self.permission_owner.has_object_permission(
                request,
                view=None,
                obj=obj
            )
        )

    def test_owner_permission_no_attributes(self):
        """Test permission when object has no user or order attribute."""

        class EmptyObj:
            pass

        obj = EmptyObj()

        request = self.factory.get("/")
        request.user = self.regular_user

        self.assertFalse(
            self.permission_owner.has_object_permission(
                request,
                view=None,
                obj=obj
            )
        )

    def test_owner_permission_anonymous_user(self):
        """Anonymous user should not be owner."""
        class MockObj:
            def __init__(self, user):
                self.user = user

        obj = MockObj(user=self.regular_user)
        request = self.factory.get("/")
        request.user = None

        self.assertFalse(
            self.permission_owner.has_object_permission(
                request,
                view=None,
                obj=obj
            )
        )