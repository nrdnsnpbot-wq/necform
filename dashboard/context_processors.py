# context_processors.py
from django.utils import timezone
from .models import Abonnement

def global_variables(request):
    today = timezone.now().date()
    cv_restants = 0
    can_download = False
    abonnement = None
    user = None
    if request.user.is_authenticated:
        user = request.user
        # récupération de l'abonnement
        if user.abonnement_type:
            try:
                abonnement = Abonnement.objects.get(type=user.abonnement_type)
                nombre_cv_limite = abonnement.nombre_cv
                cv_telecharges = user.nombre_cv_mois
                cv_restants = user.nombre_cv_peut_telecharger
                can_download = user.nombre_cv_peut_telecharger > 0 and (user.abonnement_fin and user.abonnement_fin >= today)
            except Abonnement.DoesNotExist:
                abonnement = None
                cv_restants = 0
                can_download = False

    return {
        "user": user,
        "today": today,
        "abonnement": abonnement,
        "cv_restants": cv_restants,
        "can_download": can_download,
    }
