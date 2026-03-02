from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user(self):
        """Test creating a regular user"""
        email = "test@example.com"
        password = "password123"
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email(self):
        """Test error when creating a user without an email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="password123")

        with self.assertRaises(ValueError) as cm:
            User.objects.create_user(email=None, password="password123")

        self.assertEqual(str(cm.exception), "The given email must be set")

    def test_create_superuser(self):
        """Test creating a superuser"""
        email = "admin@example.com"
        user = User.objects.create_superuser(email=email, password="password123")

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_with_invalid_permissions(self):
        """Test error when creating a superuser with incorrect permissions"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="bad_admin@example.com", password="password123", is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="bad_admin2@example.com",
                password="password123",
                is_superuser=False,
            )

    def test_email_normalization(self):
        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM", password="password123"
        )
        self.assertEqual(user.email, "TEST@example.com")

    def test_create_user_with_duplicate_email(self):
        """Test that creating a user with an existing email raises an error"""
        User.objects.create_user(email="test@example.com", password="password123")
        with self.assertRaises(Exception):  # Или IntegrityError
            User.objects.create_user(email="test@example.com", password="password456")
