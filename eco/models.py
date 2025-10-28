from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)
    coin_balance = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_coins(self, amount, description=""):
        self.coin_balance += amount
        self.save()
        CoinTransaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='earn',
            description=description
        )
    
    def spend_coins(self, amount, description=""):
        if self.coin_balance >= amount:
            self.coin_balance -= amount
            self.save()
            CoinTransaction.objects.create(
                user=self.user,
                amount=amount,
                transaction_type='spend',
                description=description
            )
            return True
        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class EcoTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    coin_reward = models.IntegerField(default=10)
    deadline = models.DateTimeField(blank=True, null=True)
    example_photo = models.ImageField(upload_to='task_examples/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    task = models.ForeignKey(EcoTask, on_delete=models.CASCADE, related_name='submissions')
    description = models.TextField()
    image = models.ImageField(upload_to='submissions/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moderator_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'task']


class CoinTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earn', 'Earn'),
        ('spend', 'Spend'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.amount} coins"
    
    class Meta:
        ordering = ['-created_at']


class MerchItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='merchandise/')
    coin_cost = models.IntegerField()
    available = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['coin_cost']


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    merch_item = models.ForeignKey(MerchItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.merch_item.name}"
    
    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.message}"
    
    class Meta:
        ordering = ['-created_at']