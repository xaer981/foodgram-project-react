from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribing')
