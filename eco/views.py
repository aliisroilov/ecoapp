from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import (
    UserProfile, EcoTask, TaskSubmission, 
    CoinTransaction, MerchItem, Order, Notification
)
from .forms import SignUpForm, UserProfileForm, TaskSubmissionForm, OrderForm


def is_moderator(user):
    return user.is_staff or user.is_superuser


def home(request):
    """Home page with stats and featured tasks"""
    total_tasks = EcoTask.objects.filter(is_active=True).count()
    total_users = UserProfile.objects.count()
    total_submissions = TaskSubmission.objects.filter(status='approved').count()
    featured_tasks = EcoTask.objects.filter(is_active=True).order_by('-coin_reward')[:3]
    
    # Get unread notifications for logged in users
    unread_notifications = []
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        )[:5]
        
        # Additional stats for logged in users
        completed_tasks = TaskSubmission.objects.filter(
            user=request.user,
            status='approved'
        ).count()
        
        # Calculate rank
        from django.contrib.auth.models import User
        all_users = User.objects.annotate(
            submission_count=Count('submissions', filter=Q(submissions__status='approved'))  # FIXED: tasksubmission -> submissions
        ).order_by('-submission_count')
        
        rank = 1
        for i, u in enumerate(all_users, 1):
            if u.id == request.user.id:
                rank = i
                break
        
        impact_score = completed_tasks * 10
    else:
        completed_tasks = 0
        rank = None
        impact_score = 0
    
    context = {
        'total_tasks': total_tasks,
        'total_users': total_users,
        'total_submissions': total_submissions,
        'featured_tasks': featured_tasks,
        'unread_notifications': unread_notifications,
        'completed_tasks': completed_tasks,
        'rank': rank,
        'impact_score': impact_score,
    }
    return render(request, 'eco/home.html', context)

def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'eco/signup.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'eco/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile page"""
    profile = request.user.profile
    recent_transactions = CoinTransaction.objects.filter(user=request.user)[:10]
    recent_submissions = TaskSubmission.objects.filter(user=request.user)[:5]
    
    # Calculate stats
    completed_tasks = TaskSubmission.objects.filter(
        user=request.user,
        status='approved'
    ).count()
    
    # Calculate rank
    from django.contrib.auth.models import User
    all_users = User.objects.annotate(
        submission_count=Count('submissions', filter=Q(submissions__status='approved'))  # FIXED: tasksubmission -> submissions
    ).order_by('-submission_count')
    
    rank = 1
    for i, u in enumerate(all_users, 1):
        if u.id == request.user.id:
            rank = i
            break
    
    impact_score = completed_tasks * 10
    
    context = {
        'profile': profile,
        'recent_transactions': recent_transactions,
        'recent_submissions': recent_submissions,
        'completed_tasks': completed_tasks,
        'rank': rank,
        'impact_score': impact_score,
    }
    return render(request, 'eco/profile.html', context)

@login_required
def edit_profile_view(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            
            # Also update User model fields
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'eco/edit_profile.html', {'form': form})


def tasks_view(request):
    """List all eco tasks with filtering and pagination"""
    tasks_list = EcoTask.objects.filter(is_active=True)
    
    # Check which tasks user has already submitted
    submitted_task_ids = []
    if request.user.is_authenticated:
        submitted_task_ids = TaskSubmission.objects.filter(
            user=request.user
        ).values_list('task_id', flat=True)
    
    # Search
    search = request.GET.get('search')
    if search:
        tasks_list = tasks_list.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        tasks_list = tasks_list.filter(difficulty=difficulty)
    
    # Sort
    sort = request.GET.get('sort')
    if sort == 'reward':
        tasks_list = tasks_list.order_by('-coin_reward')
    elif sort == 'deadline':
        tasks_list = tasks_list.order_by('deadline')
    elif sort == 'title':
        tasks_list = tasks_list.order_by('title')
    else:
        tasks_list = tasks_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tasks_list, 9)  # 9 tasks per page
    page = request.GET.get('page')
    tasks = paginator.get_page(page)
    
    context = {
        'tasks': tasks,
        'submitted_task_ids': submitted_task_ids,
    }
    return render(request, 'eco/tasks.html', context)


def task_detail_view(request, task_id):
    """Task detail page"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    
    # Check if user has already submitted this task
    user_submission = None
    if request.user.is_authenticated:
        user_submission = TaskSubmission.objects.filter(
            user=request.user,
            task=task
        ).first()
    
    context = {
        'task': task,
        'user_submission': user_submission,
    }
    return render(request, 'eco/task_detail.html', context)


@login_required
def submit_task_view(request, task_id):
    """Submit a task completion"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    
    # Check if user has already submitted this task
    existing_submission = TaskSubmission.objects.filter(
        user=request.user,
        task=task
    ).first()
    
    if existing_submission:
        messages.warning(request, 'You have already submitted this task.')
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.task = task
            submission.save()
            messages.success(request, 'Your submission has been sent for review!')
            return redirect('my_submissions')
    else:
        form = TaskSubmissionForm()
    
    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'eco/submit_task.html', context)


# NEW VIEW: My Submissions
@login_required
def my_submissions(request):
    """View user's task submissions"""
    submissions = TaskSubmission.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        submissions = submissions.filter(status=status)
    
    context = {
        'submissions': submissions,
    }
    return render(request, 'eco/my_submissions.html', context)


@login_required
@user_passes_test(is_moderator)
def moderation_dashboard(request):
    """Moderation dashboard for staff"""
    status_filter = request.GET.get('status', 'pending')
    
    submissions = TaskSubmission.objects.all().order_by('-created_at')
    if status_filter != 'all':
        submissions = submissions.filter(status=status_filter)
    
    context = {
        'submissions': submissions,
        'status_filter': status_filter,
    }
    return render(request, 'eco/moderation_dashboard.html', context)


@login_required
@user_passes_test(is_moderator)
def approve_submission(request, submission_id):
    """Approve a task submission"""
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    
    if submission.status == 'pending':
        submission.status = 'approved'
        submission.reviewed_at = timezone.now()
        submission.save()
        
        # Add coins to user
        submission.user.profile.add_coins(
            submission.task.coin_reward,
            f"Completed task: {submission.task.title}"
        )
        
        # Create notification
        Notification.objects.create(
            user=submission.user,
            message=f'Your submission for "{submission.task.title}" has been approved! You earned {submission.task.coin_reward} coins.',
            notification_type='task_approved',
            link=f'/tasks/{submission.task.id}/'
        )
        
        messages.success(request, f'Submission approved! {submission.user.username} earned {submission.task.coin_reward} coins.')
    
    return redirect('moderation_dashboard')


@login_required
@user_passes_test(is_moderator)
def reject_submission(request, submission_id):
    """Reject a task submission"""
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        submission.status = 'rejected'
        submission.moderator_comment = comment
        submission.reviewed_at = timezone.now()
        submission.save()
        
        # Create notification
        Notification.objects.create(
            user=submission.user,
            message=f'Your submission for "{submission.task.title}" was rejected.',
            notification_type='task_rejected',
            link=f'/tasks/{submission.task.id}/'
        )
        
        messages.success(request, 'Submission rejected.')
        return redirect('moderation_dashboard')
    
    context = {'submission': submission}
    return render(request, 'eco/reject_submission.html', context)


def store_view(request):
    """Merchandise store"""
    items = MerchItem.objects.filter(available=True).order_by('name')  # FIXED: removed is_popular
    
    user_balance = 0
    if request.user.is_authenticated:
        user_balance = request.user.profile.coin_balance
    
    context = {
        'items': items,
        'user_balance': user_balance,
    }
    return render(request, 'eco/store.html', context)


@login_required
def redeem_item(request, item_id):
    """Redeem a merchandise item"""
    item = get_object_or_404(MerchItem, id=item_id, available=True)
    profile = request.user.profile
    
    if request.method == 'POST':
        if profile.coin_balance >= item.coin_cost:
            # Get shipping address
            shipping_address = request.POST.get('shipping_address', '')
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                merch_item=item,
                shipping_address=shipping_address
            )
            
            # Deduct coins
            profile.spend_coins(
                item.coin_cost,
                f"Redeemed: {item.name}"
            )
            
            # Update stock
            if hasattr(item, 'stock_quantity') and item.stock_quantity:
                item.stock_quantity -= 1
                if item.stock_quantity <= 0:
                    item.available = False
                item.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                message=f'You successfully redeemed {item.name} for {item.coin_cost} coins!',
                notification_type='order_placed',
                link='/orders/'
            )
            
            messages.success(request, f'Successfully redeemed {item.name}!')
            return redirect('my_orders')
        else:
            messages.error(request, 'Insufficient coins!')
            return redirect('store')
    
    context = {
        'item': item,
    }
    return render(request, 'eco/redeem_item.html', context)


# NEW VIEW: My Orders (alias for orders_view)
@login_required
def my_orders(request):
    """User's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'eco/my_orders.html', context)


@login_required
def orders_view(request):
    """User's orders (same as my_orders)"""
    return my_orders(request)


# NEW VIEW: Transactions History
@login_required
def transactions(request):
    """View user's coin transaction history"""
    transactions_list = CoinTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(transactions_list, 20)  # 20 transactions per page
    page = request.GET.get('page')
    transactions_page = paginator.get_page(page)
    
    context = {
        'transactions': transactions_page,
    }
    return render(request, 'eco/transactions.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('home')


@login_required
@user_passes_test(is_moderator)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    from django.contrib.auth.models import User
    
    # Top users by submissions
    top_users = User.objects.annotate(
        submission_count=Count('submissions', filter=Q(submissions__status='approved'))  # FIXED
    ).order_by('-submission_count')[:5]
    
    # Most completed tasks
    top_tasks = EcoTask.objects.annotate(
        completion_count=Count('submissions', filter=Q(submissions__status='approved'))  # FIXED
    ).order_by('-completion_count')[:5]
    
    # Most redeemed items
    top_items = MerchItem.objects.annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:5]
    
    # General stats
    total_users = User.objects.count()
    total_tasks = EcoTask.objects.count()
    total_submissions = TaskSubmission.objects.count()
    pending_submissions = TaskSubmission.objects.filter(status='pending').count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    context = {
        'top_users': top_users,
        'top_tasks': top_tasks,
        'top_items': top_items,
        'total_users': total_users,
        'total_tasks': total_tasks,
        'total_submissions': total_submissions,
        'pending_submissions': pending_submissions,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'eco/admin_dashboard.html', context)

@login_required
@user_passes_test(is_moderator)
def manage_orders(request):
    """Manage all orders"""
    status_filter = request.GET.get('status', 'pending')
    
    orders = Order.objects.all().order_by('-created_at')
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'eco/manage_orders.html', context)


@login_required
@user_passes_test(is_moderator)
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Create notification
            Notification.objects.create(
                user=order.user,
                message=f'Your order for {order.merch_item.name} is now {new_status}.',
                notification_type='order_update',
                link='/orders/'
            )
            
            messages.success(request, f'Order status updated to {new_status}.')
    
    return redirect('manage_orders')