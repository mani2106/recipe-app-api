"""
Serializers (to<-->from python object) for user API View
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

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


class UserAuthTokenSerializer(serializers.Serializer):
    """Serializer for user auth token"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate user"""

        email = attrs.get('email')
        pwd = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=pwd
        )

        if not user:
            msg = _('Unable to authenticate with given credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
