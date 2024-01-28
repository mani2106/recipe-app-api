"""
Serializers (to<-->from python object) for user API View
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        """Info for restframework to serialize custom models"""
        model = get_user_model()
        # fields to save in model
        fields = ['email', 'password', 'name']
        # not using the is_staff like meta args
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return user with encrypted pwd"""
        return get_user_model().objects.create_user(**validated_data)
