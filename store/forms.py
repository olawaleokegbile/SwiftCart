from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from .models import Profile

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super().save(request)  # Allauth creates the user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Optionally: Update Customer object
        customer = user.customer
        customer.name = f"{user.first_name} {user.last_name}"
        customer.save()

        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "address", "profile_picture"]