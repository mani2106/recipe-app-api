"""
Serializers for Recipes
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for Ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipes"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price',
                  'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_obj(self, objs, recipe, obj_name='Tag'):
        """Handles getting or creating tags as needed"""
        auth_user = self.context['request'].user
        model = Tag if obj_name == 'Tag' else Ingredient
        attrib = 'tags' if obj_name == 'Tag' else 'ingredients'
        for obj in objs:
            db_obj, _ = model.objects.get_or_create(
                user=auth_user,
                **obj
            )

            # recipe.tags.add(db_obj)
            getattr(recipe, attrib).add(db_obj)

    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop('tags', [])
        ingrs = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_obj(recipe=recipe, objs=tags)
        self._get_or_create_obj(recipe=recipe, objs=ingrs,
                                obj_name='Ingredients')
        return recipe

    def update(self, instance, validated_data):
        """Update recipe"""
        tags = validated_data.pop('tags', None)
        ingrs = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_obj(tags, instance)

        if ingrs is not None:
            instance.tags.clear()
            self._get_or_create_obj(ingrs, instance, obj_name='Ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe Details"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['desc']
