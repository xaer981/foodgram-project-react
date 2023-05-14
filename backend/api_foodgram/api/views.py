from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilters
from .paginators import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SubscriptionSerializer,
                          TagSerializer, User)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class UserViewSet(UserViewSet):
    """
    Кастомный вьюсет наследованный от стандартного вьюсета Djoser.
    Отключены ненужные функции(ресет пароля, изменение юзернейма и т.д.)
    В action 'me' оставлена только возможность get-запроса.
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
