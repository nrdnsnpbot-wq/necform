from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_front, name='index_front'),
    path('indexx', views.index_front, name='index_front'),
    path('', views.index_front, name='index'),
    path('login', views.login_view, name='login'),
    path('home/', views.index, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path("scanner-cv/", views.scanner_cv, name="scanner_cv"),
    path("importcv/", views.index, name="importcv"),
    path('dashboard/', include('dashboard.urls')),
    path('signup/', views.signup_view, name='signup'), 
    path("accounts/", include("allauth.urls")),
    path("contact/", views.contact_view, name="contact"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
