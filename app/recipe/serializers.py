"""
Serializers for Recipes
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipes"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_min', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe Details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields = ['desc']
