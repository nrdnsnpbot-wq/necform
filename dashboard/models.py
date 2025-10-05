from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class ContactMessage(models.Model):
    first_name = models.CharField("First name", max_length=100)
    last_name = models.CharField("Last name", max_length=100)
    email = models.EmailField("Votre email")
    phone = models.CharField("Phone number", max_length=20, blank=True, null=True)
    message = models.TextField("Message")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message de {self.first_name} {self.last_name} ({self.email})"

class Abonnement(models.Model):
    TYPE_CHOICES = [
        ("Basique", "Basique"),
        ("Standard", "Standard"),
        ("Premium", "Premium"),
    ]

    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        unique=True
    )
    prix_euros = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.00,
        help_text="Prix de l'abonnement en euros (€)"
    )
    duree_jours = models.PositiveIntegerField(
        default=30, 
        help_text="Durée de validité de l'abonnement en jours"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        default="",
        help_text="Écris une ligne par fonctionnalité (une ligne = un avantage)"
    )

    nombre_cv = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de CV téléchargeables avec cet abonnement"
    )

    # --- Utils ---
    def prix_cents(self):
        """Stripe utilise les centimes (ex: 9.99€ → 999)."""
        return int(self.prix_euros * 100)

    def get_description_list(self):
        """Retourne la description en liste de lignes utilisables dans le template."""
        return [line.strip() for line in self.description.split("\n") if line.strip()]

    def __str__(self):
        return f"{self.type} - {self.prix_euros}€ / {self.duree_jours} jours"

# --- Utilisateur (entreprise / admin / staff) ---
class User(AbstractUser):
    # Type de user
    TYPE_CHOICES = [
        ('entreprise', 'Entreprise'),
        ('superadmin', 'Super Admin'),
    ]
    type_de_user = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='entreprise'
    )

    # Infos de l’entreprise
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    company_phone = models.CharField(max_length=50, blank=True, null=True)
    company_kbis = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    # Statistiques
    cv_download_count = models.PositiveIntegerField(default=0)
    nombre_cv_total = models.PositiveIntegerField(default=0)
    nombre_cv_mois = models.PositiveIntegerField(default=0)
    nombre_cv_peut_telecharger = models.PositiveIntegerField(default=0)

    # Abonnement
    abonnement_type = models.CharField(max_length=50, blank=True, null=True)
    abonnement_debut = models.DateField(default=timezone.now)
    abonnement_fin = models.DateField(null=True,default=timezone.now, blank=True)  # date actuelle par défaut

    def __str__(self):
        return self.username


# --- Candidat lié à une entreprise (User) ---
class Candidat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidats")

    # Informations de base
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    titre_poste = models.CharField(max_length=150, blank=True, null=True)
    description_profil = models.TextField(blank=True, null=True)

    # Autres sections
    langues = models.TextField(blank=True, null=True)      
    experience = models.TextField(blank=True, null=True)   
    certificats = models.TextField(blank=True, null=True)
    formation = models.TextField(blank=True, null=True)  
    competences = models.TextField(blank=True, null=True)
    informations_contact = models.TextField(blank=True, null=True)  

    # Champ libre
    rajouter_champ = models.TextField(blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.titre_poste or 'Sans titre'}"
