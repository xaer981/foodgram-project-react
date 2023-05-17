from django.contrib import admin

from .models import (Favorite, Ingredient, MeasureUnit, Recipe,
                     RecipeIngredient, RecipeTag, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(MeasureUnit)
class MeasureUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'in_favorites',)
    readonly_fields = ('in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [RecipeIngredientInline, RecipeTagInline]

    @admin.display(description='Количество добавлений в избранное')
    def in_favorites(self, obj):

        return obj.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
