"""Données du tableau de bord et du badge « Messages » de l'admin (thème Unfold)."""

from .models import Article, Competence, Experience, Message, Projet, Technologie


def badge_messages(request):
    non_lus = Message.objects.filter(lu=False).count()
    return str(non_lus) if non_lus else None


AJOUTS = [
    {"titre": "Expérience", "aide": "Un poste, un stage, une mission", "icone": "work", "url": "admin:portfolio_experience_add"},
    {"titre": "Formation", "aide": "Un diplôme ou un cursus", "icone": "school", "url": "admin:portfolio_formation_add"},
    {"titre": "Certification", "aide": "Un certificat obtenu", "icone": "workspace_premium", "url": "admin:portfolio_certification_add"},
    {"titre": "Compétence", "aide": "Avec son niveau et sa catégorie", "icone": "bolt", "url": "admin:portfolio_competence_add"},
    {"titre": "Projet", "aide": "Une réalisation à montrer", "icone": "rocket_launch", "url": "admin:portfolio_projet_add"},
]


def dashboard_callback(request, context):
    context["ajouts"] = AJOUTS
    context.update(
        {
            "non_lus": Message.objects.filter(lu=False).count(),
            "derniers_messages": Message.objects.order_by("-date")[:5],
            "nb_projets": Projet.objects.count(),
            "nb_a_la_une": Projet.objects.filter(a_la_une=True).count(),
            "projets_recents": Projet.objects.prefetch_related("technologies").order_by("-date")[:5],
            "nb_articles": Article.objects.filter(publie=True).count(),
            "nb_brouillons": Article.objects.filter(publie=False).count(),
            "nb_experiences": Experience.objects.filter(type=Experience.Type.PRO).count(),
            "nb_formations": Experience.objects.filter(type=Experience.Type.FORMATION).count(),
            "nb_certifications": Experience.objects.filter(type=Experience.Type.CERTIFICATION).count(),
            "nb_competences": Competence.objects.count(),
            "nb_technologies": Technologie.objects.count(),
        }
    )
    return context
