from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .constants import DATE_FORMAT
from .filters import IngredientFilter, RecipeFilters
from .paginators import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SubscriptionSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import CustomUser as User
from users.models import Subscription


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для /api/ingredients/*.
    Доступен для чтения всем, для ред-я и создания: только админу.
    Позволяет производить поиск по вхождению в начало поля name.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для /api/recipes/*.
    Доступен для чтения всем, для ред-я автору объекта или админу.
    Создавать объект могут только аутентифицированные.
    Фильтруется по:
    - выбору из предустановленных поля tags,
    - по булеву значению полей is_favorited и is_in_shopping_cart(1 или 0).
    Три дополнительные actions для аутентифицированных:
    favorite - добавить/удалить рецепт в/из избранное(ого),
    shopping_cart - добавить/удалить рецепт в/из корзину(ы) покупок,
    download_shopping_cart - скачать список ингредиентов
    для всех рецептов в корзине покупок.
    """
    queryset = Recipe.objects.prefetch_related('tags', 'ingredients')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters
    pagination_class = PageLimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        if request.method == 'POST':

            return self.add_to(Favorite, request.user, pk)

        return self.delete_from(Favorite, request.user, pk)

    @action(['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        if request.method == 'POST':

            return self.add_to(ShoppingCart, request.user, pk)

        return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__pk=pk).exists():
            return Response({'errors': 'Нельзя добавит рецепт дважды'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__pk=pk)
        if obj.exists():
            obj.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Нельзя удалить то, чего нет'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response({'errors': 'Ваша корзина покупок пуста.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit__name'
            ).annotate(amount=Sum('amount'))
        current_date = datetime.today().date().strftime(DATE_FORMAT)
        shopping_cart = [f'Корзина покупок для '
                         f'{user.get_full_name()} от {current_date}\n']
        for ingredient in ingredients:
            shopping_cart.append(
                f'- {ingredient["ingredient__name"]}: {ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit__name"]}')
        shopping_cart.append('\nКорзина собрана в FoodGram')
        shopping_cart = '\n'.join(shopping_cart)
        file_name = f'{user.username}_shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для /api/tags/*.
    Доступ для чтения: всем, ред-е и создание: только админу.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для /api/users/*.
    Кастомный вьюсет наследованный от стандартного вьюсета Djoser.
    Отключены ненужные функции(ресет пароля, изменение юзернейма и т.д.)
    В action 'me' оставлена только возможность get-запроса.
    Две дополнительные actions для аутентифицированных:
    subscribe - подписаться/отписаться на(от) автора,
    subscriptions - вывести список подписок и их рецептов.
    """
    pagination_class = PageLimitPagination
    resend_activation = None
    reset_password = None
    reset_password_confirm = None
    set_username = None
    reset_username = None
    reset_username_confirm = None

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):

        return super().me(request, *args, **kwargs)

    @action(['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        subscribing = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(subscribing,
                                                data=request.data,
                                                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, subscribing=subscribing)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(Subscription,
                                         user=user,
                                         subscribing=subscribing)
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(
            subscribing__user=user).prefetch_related('recipes')
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(pages,
                                            many=True,
                                            context={'request': request})

        return self.get_paginated_response(serializer.data)
