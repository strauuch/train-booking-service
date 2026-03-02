from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import extend_schema, extend_schema_view

from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Register a new user",
        description="Creates a new user account with an email and password.",
    )
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema_view(
    get=extend_schema(
        summary="Get current user profile",
        description="Returns the details of the currently authenticated user.",
    ),
    put=extend_schema(
        summary="Update user profile",
        description="Updates the profile information for the authenticated user.",
    ),
    patch=extend_schema(
        summary="Partially update user profile",
        description="Partially updates the profile information for the authenticated user.",
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
