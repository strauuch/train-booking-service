from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.admin.sites import site

from user.admin import CustomUserAdmin

User = get_user_model()


class CustomUserAdminTests(TestCase):

    def setUp(self):
        self.admin_class = CustomUserAdmin(User, site)

    def test_user_registered_in_admin(self):
        """Check that User model is registered in admin"""
        self.assertIn(User, site._registry)

    def test_list_display(self):
        """Check list_display configuration"""
        expected = ("email", "first_name", "last_name", "is_staff")
        self.assertEqual(self.admin_class.list_display, expected)

    def test_search_fields(self):
        """Check search_fields configuration"""
        expected = ("email",)
        self.assertEqual(self.admin_class.search_fields, expected)

    def test_ordering(self):
        """Check ordering configuration"""
        expected = ("email",)
        self.assertEqual(self.admin_class.ordering, expected)

    def test_fieldsets_structure(self):
        """Check admin fieldsets structure"""

        expected_fieldsets = (
            (None, {"fields": ("email", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name")}),
            (
                "Permissions",
                {
                    "fields": (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                },
            ),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )

        # gettext_lazy(_) returns proxy object — convert to str
        actual = tuple(
            (str(name) if name is not None else None, data)
            for name, data in self.admin_class.fieldsets
        )

        self.assertEqual(expected_fieldsets, actual)