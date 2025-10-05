from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))
    company_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Company Name"}))
    company_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Phone"}))

    class Meta:
        model = User
        fields = ("username", "email", "company_name", "company_phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type_de_user = "entreprise"   
        user.abonnement_type = "aucun"   
        user.abonnement_fin = None 
        user.cv_download_count = 0
        user.nombre_cv_total = 0
        user.nombre_cv_mois = 0
        if commit:
            user.save()
        return user

from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "phone", "message"]

        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name", "class": "form-control"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Votre email", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number", "class": "form-control"}),
            "message": forms.Textarea(attrs={"placeholder": "Message", "class": "form-control", "rows": 5}),
        }
