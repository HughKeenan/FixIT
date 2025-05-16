from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class SignUpForm(UserCreationForm):
    year_of_birth = forms.IntegerField(
        label="Year of Birth",
        min_value=1900,
        max_value=2025,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 1985'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit)
        # Ensure profile is created here, not by signal
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.year_of_birth = self.cleaned_data['year_of_birth']
        profile.save()
        return user