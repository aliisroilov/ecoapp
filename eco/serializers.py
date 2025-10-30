from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, EcoTask, TaskSubmission,
    MerchItem, Order, CoinTransaction, Notification
)

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
    
    def get_profile(self, obj):
        return {
            'coin_balance': obj.profile.coin_balance,
            'photo': obj.profile.photo.url if obj.profile.photo else None,
            'location': obj.profile.location,
            'bio': obj.profile.bio,
        }

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoTask
        fields = '__all__'

class TaskSubmissionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    
    class Meta:
        model = TaskSubmission
        fields = '__all__'

class MerchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    merch_item = MerchItemSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
