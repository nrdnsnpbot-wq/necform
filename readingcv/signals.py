# readingcv/signals.py

from allauth.account.signals import user_signed_up
from django.dispatch import receiver
import uuid

@receiver(user_signed_up)
def populate_user_profile(request, user, **kwargs):
    """
    Quand un utilisateur s'inscrit via Google (ou autre provider),
    si aucun username n'est défini, on génère un identifiant unique automatiquement.
    """
    if not user.username:
        # Générer un username du type user_ab12cd34
        user.username = f"user_{uuid.uuid4().hex[:8]}"
        user.save()
