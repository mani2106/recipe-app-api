"""
Views for User API
"""
from rest_framework import generics

from .serializer import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""
    # Setting custom serializer
    serializer_class = UserSerializer
