from rest_framework import serializers

from recipes.models import Ingredient, Tag


def ingredients_tags_in_recipe_validator(ingredients, tags):
    """
    Проверяет ингредиенты и тэги на валидность.
    Выдаёт ошибку в случаях:
    - отсутствия ингредиентов или тэгов в запросе
    - отстутствия ингредиентов или тэгов в БД
    - использования повторяющихся ингредиентов/тэгов в запросе
    - количества ингредиента <= 0.
    """
    if not ingredients:
        raise serializers.ValidationError({'ingredients': (
            'Укажите хотя бы один ингредиент.')})
    if not tags:
        raise serializers.ValidationError({'tags': (
            'Укажите хотя бы один тэг.')})

    ingredients_list = []
    for cur_ingredient in ingredients:
        try:
            ingredient = Ingredient.objects.get(id=cur_ingredient['id'])
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError({'ingredients': (
                f'Ингредиент с id {cur_ingredient["id"]} не существует.')})

        if ingredient in ingredients_list:
            raise serializers.ValidationError({'ingredients': (
                f'Ингредиенты в рецепте не могут повторяться '
                f'(ID - {ingredient.id}).')})

        ingredients_list.append(ingredient)

        if cur_ingredient.get('amount') <= 0:
            raise serializers.ValidationError({'ingredients': (
                f'Количество ингредиента c id {cur_ingredient["id"]} '
                'не может быть меньше или равно 0.')})

    tags_list = []
    for cur_tag in tags:
        try:
            tag = Tag.objects.get(id=cur_tag)
        except Tag.DoesNotExist:
            raise serializers.ValidationError({'tags': (
                f'Тэг с id {cur_tag} не существует.')})

        if tag in tags_list:
            raise serializers.ValidationError({'tags': (
                f'Тэги не могут повторяться (ID - {tag.id}).')})

        tags_list.append(tag)
