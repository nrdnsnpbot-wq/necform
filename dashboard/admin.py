from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Abonnement, ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "message")
    readonly_fields = ("created_at",)
    list_filter = ("created_at",)

    fieldsets = (
        ("Informations personnelles", {
            "fields": ("first_name", "last_name", "email", "phone")
        }),
        ("Message", {
            "fields": ("message",)
        }),
        ("Date", {
            "fields": ("created_at",)
        }),
    )

class CustomUserAdmin(UserAdmin):
    # Colonnes visibles dans la liste des users
    list_display = (
        'username',
        'email',
        'type_de_user',
        'abonnement_type',
        'abonnement_fin',
        'nombre_cv_peut_telecharger',  # ✅ ajouté ici
        'is_active',
    )
    list_filter = ('type_de_user', 'abonnement_type', 'is_active')
    search_fields = ('username', 'email', 'company_name')
    ordering = ('-date_joined',)

    # Organisation des champs dans le formulaire admin
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name')}),
        ('Entreprise', {'fields': ('company_name', 'company_phone')}),
        (
            'Abonnement',
            {
                'fields': (
                    'abonnement_type',
                    'abonnement_debut',
                    'abonnement_fin',
                    'nombre_cv_peut_telecharger',  # ✅ ajouté ici
                )
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'type_de_user',
                # ⚠️ ici tu peux ajouter 'nombre_cv_peut_telecharger'
                # mais en général on le laisse calculé automatiquement
            ),
        }),
    )

    # Permissions custom que tu avais déjà
    def has_module_permission(self, request):
        return request.user.is_active and request.user.type_de_user != 'entreprise'

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.type_de_user != 'entreprise'

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.type_de_user != 'entreprise'

    def has_add_permission(self, request):
        return request.user.is_active and request.user.type_de_user != 'entreprise'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.type_de_user != 'entreprise'


class AbonnementAdmin(admin.ModelAdmin):
    list_display = ("type", "prix_euros", "duree_jours", "description")
    list_editable = ("prix_euros", "duree_jours", "description")
    search_fields = ("type",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Abonnement, AbonnementAdmin)
