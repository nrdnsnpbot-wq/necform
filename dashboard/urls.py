from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.index, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path("scanner-cv/", views.scanner_cv, name="scanner_cv"),
    path("importcv/", views.index, name="importcv"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("candidats/", views.candidats_list, name="candidats_list"),
    path('abonnement/', views.abonnement_view, name='abonnement'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success_payment, name='success_payment'),
    path('cancel/', views.cancel_payment, name='cancel_payment'),
    path('telecharger-cv/', views.telecharger_cv, name='telecharger_cv'),
    path("signup/", views.signup_view, name="signup"),
    path("contact/", views.contact_view, name="contact"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
