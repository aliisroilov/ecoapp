from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, TaskSubmission, Order


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
        'placeholder': 'Email address'
    }))
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
        'placeholder': 'Last name'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
            'placeholder': 'Confirm password'
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo', 'location', 'age', 'bio']
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'placeholder': 'Your location'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'placeholder': 'Your age'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'placeholder': 'Tell us about yourself',
                'rows': 4
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition'
            })
        }


class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'placeholder': 'Describe how you completed this task...',
                'rows': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'accept': 'image/*'
            })
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition',
                'placeholder': 'Enter your full shipping address',
                'rows': 4
            })
        }