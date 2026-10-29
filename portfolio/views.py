import logging
from itertools import groupby

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import Article, Competence, Experience, Projet, Technologie

logger = logging.getLogger(__name__)


def _grouper_competences():
    """Regroupe les compétences par catégorie, dans l'ordre de déclaration des choix."""
    rang = {cat: i for i, cat in enumerate(Competence.Categorie.values)}
    competences = sorted(Competence.objects.all(), key=lambda c: (rang[c.categorie], c.ordre, -c.niveau))
    libelles = dict(Competence.Categorie.choices)
    return [(libelles[cat], list(items)) for cat, items in groupby(competences, key=lambda c: c.categorie)]


def accueil(request):
    experiences = Experience.objects.all()
    context = {
        "projets": Projet.objects.filter(a_la_une=True).prefetch_related("technologies")[:6],
        "competences": _grouper_competences(),
        "parcours_pro": [e for e in experiences if e.type == Experience.Type.PRO],
        "formations": [e for e in experiences if e.type == Experience.Type.FORMATION],
        "certifications": [e for e in experiences if e.type == Experience.Type.CERTIFICATION],
        "articles": Article.objects.publies()[:3] if settings.PORTFOLIO["blog_actif"] else [],
        "form": ContactForm(),
    }
    return render(request, "portfolio/accueil.html", context)


def projets(request):
    qs = Projet.objects.prefetch_related("technologies")
    techno = request.GET.get("techno")
    if techno:
        qs = qs.filter(technologies__nom=techno)
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    return render(
        request,
        "portfolio/projets.html",
        {
            "page": page,
            "techno_active": techno,
            "technologies": Technologie.objects.filter(projets__isnull=False).distinct(),
        },
    )


def projet(request, slug):
    obj = get_object_or_404(Projet.objects.prefetch_related("technologies"), slug=slug)
    autres = Projet.objects.exclude(pk=obj.pk)[:3]
    return render(request, "portfolio/projet.html", {"projet": obj, "autres": autres})


def blog(request):
    if not settings.PORTFOLIO["blog_actif"]:
        raise Http404
    page = Paginator(Article.objects.publies(), 6).get_page(request.GET.get("page"))
    return render(request, "portfolio/blog.html", {"page": page})


def article(request, slug):
    if not settings.PORTFOLIO["blog_actif"]:
        raise Http404
    obj = get_object_or_404(Article.objects.publies(), slug=slug)
    return render(request, "portfolio/article.html", {"article": obj})


def contact(request):
    if request.method != "POST":
        return render(request, "portfolio/contact.html", {"form": ContactForm()})

    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, "portfolio/contact.html", {"form": form}, status=400)

    if not form.est_spam():
        msg = form.save()
        if settings.CONTACT_NOTIFY_EMAIL:
            try:
                send_mail(
                    f"[Portfolio] {msg.sujet}",
                    f"De : {msg.nom} <{msg.email}>\n\n{msg.contenu}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_NOTIFY_EMAIL],
                )
            except Exception:
                # Le message reste enregistré et consultable dans l'admin.
                logger.exception("Échec de l'envoi de la notification de contact")
    messages.success(request, "Merci ! Votre message a bien été envoyé, je vous réponds rapidement.")
    return redirect("portfolio:contact")
