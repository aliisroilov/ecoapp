from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Tasks
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/submit/', views.submit_task_view, name='submit_task'),
    
    # Moderation
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/approve/<int:submission_id>/', views.approve_submission, name='approve_submission'),
    path('moderation/reject/<int:submission_id>/', views.reject_submission, name='reject_submission'),
    
    # Store & Orders
    path('store/', views.store_view, name='store'),
    path('store/redeem/<int:item_id>/', views.redeem_item, name='redeem_item'),
    path('orders/', views.orders_view, name='orders'),
    
    # Notifications
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/orders/', views.manage_orders, name='manage_orders'),
    path('admin-dashboard/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
]