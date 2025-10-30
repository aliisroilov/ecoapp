from django.urls import path
from . import api_views

urlpatterns = [
    # Auth endpoints
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/signup/', api_views.signup_view, name='api_signup'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    path('auth/user/', api_views.current_user_view, name='api_current_user'),
    
    # Task endpoints
    path('tasks/', api_views.task_list, name='api_task_list'),
    path('tasks/<int:pk>/', api_views.task_detail, name='api_task_detail'),
    path('tasks/<int:pk>/submit/', api_views.submit_task, name='api_submit_task'),
    path('submissions/my/', api_views.my_submissions, name='api_my_submissions'),
    
    # Store endpoints
    path('store/', api_views.store_items, name='api_store_items'),
    path('store/<int:pk>/', api_views.store_item_detail, name='api_store_item_detail'),
    path('store/<int:pk>/redeem/', api_views.redeem_item, name='api_redeem_item'),
    path('orders/my/', api_views.my_orders, name='api_my_orders'),
    
    # Profile endpoints
    path('profile/', api_views.profile_view, name='api_profile'),
    path('profile/transactions/', api_views.coin_transactions, name='api_transactions'),
    
    # Notifications
    path('notifications/', api_views.notifications_list, name='api_notifications'),
    path('notifications/<int:pk>/read/', api_views.mark_notification_read, name='api_mark_read'),
    path('notifications/read-all/', api_views.mark_all_read, name='api_mark_all_read'),
    
    # Stats
    path('stats/dashboard/', api_views.dashboard_stats, name='api_dashboard'),
    path('stats/leaderboard/', api_views.leaderboard, name='api_leaderboard'),
]
