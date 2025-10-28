from django.contrib import admin
from .models import (
    UserProfile, EcoTask, TaskSubmission, 
    CoinTransaction, MerchItem, Order, Notification
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'age', 'coin_balance']
    search_fields = ['user__username', 'location']
    list_filter = ['location']


@admin.register(EcoTask)
class EcoTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'coin_reward', 'deadline', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'task__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'created_at'


@admin.register(MerchItem)
class MerchItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'coin_cost', 'available', 'stock_quantity', 'created_at']
    list_filter = ['available', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'merch_item', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'merch_item__name']
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    date_hierarchy = 'created_at'
