from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .traitement_cv import extraire_infos_depuis_cv
from django.contrib.auth.forms import UserCreationForm
from dashboard.models import Abonnement  
from dashboard.forms import ContactMessageForm

def contact_view(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Message envoyé avec succès !")
            return redirect("indexx")  # Redirige vers la même page après envoi
    else:
        form = ContactMessageForm()

    return render(request, "dashboard/index.html", {"form": form})

def index(request):
    return render(request, 'dashboard/importcv.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  
        else:
            messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect.')
    
    return render(request, 'dashboard/login.html')  

from dashboard.forms import ContactMessageForm

def index_front(request):
    abonnements = Abonnement.objects.all()
    
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Message envoyé avec succès !")
            return redirect('index')  # ou le nom de ton URL pour index_front
    else:
        form = ContactMessageForm()
    
    return render(request, 'dashboard/index.html', {
        'abonnements': abonnements,
        'form': form,
    })
@csrf_exempt
def scanner_cv(request):
    if request.method == "POST":
        cv_file = request.FILES.get("cv_file")
        if not cv_file:
            return JsonResponse({"success": False, "error": "Aucun fichier reçu."})

        data = extraire_infos_depuis_cv(cv_file)
        if not data:
            return JsonResponse({"success": False, "error": "Impossible d'extraire les infos."})

        return JsonResponse({"success": True, **data})

    return JsonResponse({"success": False, "error": "Méthode invalide."})

from dashboard.forms import CustomUserCreationForm

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully! Please log in.")
            return redirect("login")  
    else:
        form = CustomUserCreationForm()
    return render(request, "dashboard/signup.html", {"form": form})
