from django.conf import settings

from .models import Projet


def site(request):
    # Tant qu'aucun projet n'est publié, les liens vers la section Projets sont masqués.
    return {"site": settings.PORTFOLIO, "a_des_projets": Projet.objects.exists()}
