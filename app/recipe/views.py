"""
Views for Recipe apis
"""

from rest_framework import (
    viewsets,
    mixins
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipe data in db"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes of authorized user"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


# mixins should be inherited before viewsets
class TagViewSet(mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):

    """Manage tags in db"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags of authorised user"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')


# mixins should be inherited before viewsets
class IngredientViewSet(mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):

    """Manage Ingredients in db"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Ingredients of authorised user"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')
