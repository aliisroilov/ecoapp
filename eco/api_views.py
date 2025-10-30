from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from .models import (
    UserProfile, EcoTask, TaskSubmission, 
    MerchItem, Order, CoinTransaction, Notification
)
from .serializers import (
    UserSerializer, ProfileSerializer, TaskSerializer,
    TaskSubmissionSerializer, MerchItemSerializer, 
    OrderSerializer, CoinTransactionSerializer, NotificationSerializer
)

# ============== AUTH VIEWS ==============

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': {
                    'coin_balance': profile.coin_balance,
                    'photo': profile.photo.url if profile.photo else None,
                    'location': profile.location,
                }
            }
        })
    return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # UserProfile should be created automatically via signal
    token, _ = Token.objects.get_or_create(user=user)
    profile = user.profile
    
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    }, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    return Response(UserSerializer(request.user).data)

# ============== TASK VIEWS ==============

@api_view(['GET'])
@permission_classes([AllowAny])
def task_list(request):
    tasks = EcoTask.objects.filter(is_active=True)
    
    # Apply filters
    difficulty = request.GET.get('difficulty')
    if difficulty:
        tasks = tasks.filter(difficulty=difficulty)
    
    featured = request.GET.get('featured')
    if featured:
        tasks = tasks.filter(is_featured=True)
    
    serializer = TaskSerializer(tasks, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def task_detail(request, pk):
    try:
        task = EcoTask.objects.get(pk=pk, is_active=True)
        return Response(TaskSerializer(task).data)
    except EcoTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_task(request, pk):
    try:
        task = EcoTask.objects.get(pk=pk, is_active=True)
    except EcoTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)
    
    # Create submission
    submission = TaskSubmission.objects.create(
        user=request.user,
        task=task,
        description=request.data.get('description', ''),
        image=request.FILES.get('image')
    )
    
    return Response(
        TaskSubmissionSerializer(submission).data,
        status=201
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_submissions(request):
    submissions = TaskSubmission.objects.filter(user=request.user)
    serializer = TaskSubmissionSerializer(submissions, many=True)
    return Response({'results': serializer.data})

# ============== STORE VIEWS ==============

@api_view(['GET'])
@permission_classes([AllowAny])
def store_items(request):
    items = MerchItem.objects.filter(available=True)
    serializer = MerchItemSerializer(items, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def store_item_detail(request, pk):
    try:
        item = MerchItem.objects.get(pk=pk)
        return Response(MerchItemSerializer(item).data)
    except MerchItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_item(request, pk):
    try:
        item = MerchItem.objects.get(pk=pk, available=True)
    except MerchItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)
    
    profile = request.user.profile
    
    # Check balance
    if profile.coin_balance < item.coin_cost:
        return Response({'error': 'Insufficient coins'}, status=400)
    
    # Check stock
    if item.stock_quantity <= 0:
        return Response({'error': 'Out of stock'}, status=400)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        merch_item=item,
        shipping_address=request.data.get('shipping_address', '')
    )
    
    # Deduct coins
    profile.coin_balance -= item.coin_cost
    profile.save()
    
    # Update stock
    item.stock_quantity -= 1
    item.save()
    
    # Record transaction
    CoinTransaction.objects.create(
        user=request.user,
        amount=-item.coin_cost,
        transaction_type='spend',
        description=f'Redeemed: {item.name}'
    )
    
    return Response(OrderSerializer(order).data, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response({'results': serializer.data})

# ============== PROFILE VIEWS ==============

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = request.user.profile
    
    if request.method == 'GET':
        return Response(ProfileSerializer(profile).data)
    
    elif request.method == 'PUT':
        # Update profile
        profile.location = request.data.get('location', profile.location)
        profile.bio = request.data.get('bio', profile.bio)
        
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
        
        profile.save()
        return Response(ProfileSerializer(profile).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coin_transactions(request):
    transactions = CoinTransaction.objects.filter(user=request.user)
    serializer = CoinTransactionSerializer(transactions, many=True)
    return Response({'results': serializer.data})

# ============== STATS VIEWS ==============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    profile = request.user.profile
    
    completed = TaskSubmission.objects.filter(
        user=request.user, 
        status='approved'
    ).count()
    
    total_earned = CoinTransaction.objects.filter(
        user=request.user,
        transaction_type='earn'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate rank
    all_users = User.objects.annotate(
        submission_count=Count('tasksubmission', filter=Q(tasksubmission__status='approved'))
    ).order_by('-submission_count')
    
    rank = 1
    for i, u in enumerate(all_users, 1):
        if u.id == request.user.id:
            rank = i
            break
    
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return Response({
        'completed_tasks': completed,
        'total_coins_earned': total_earned,
        'rank': rank,
        'impact_score': completed * 10,  # Example calculation
        'unread_notifications': unread_notifications,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    top_users = User.objects.annotate(
        submission_count=Count('tasksubmission', filter=Q(tasksubmission__status='approved'))
    ).order_by('-submission_count')[:10]
    
    leaderboard_data = [
        {
            'rank': i + 1,
            'username': user.username,
            'first_name': user.first_name,
            'completed_tasks': user.submission_count,
            'photo': user.profile.photo.url if user.profile.photo else None,
        }
        for i, user in enumerate(top_users)
    ]
    
    return Response({'results': leaderboard_data})

# ============== NOTIFICATION VIEWS ==============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'results': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})
