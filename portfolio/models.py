from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

MAX_IMAGE_SIDE = 1600


def reduire_image(field):
    """Redimensionne et recompresse une image envoyée pour économiser l'espace disque."""
    if not field or getattr(field, "_committed", True):
        return
    img = Image.open(field)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=82, optimize=True)
    nom = Path(field.name).stem + ".jpg"
    field.save(nom, ContentFile(buffer.getvalue()), save=False)


class SlugMixin(models.Model):
    """Génère un slug unique à partir du titre s'il est laissé vide."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titre)[:200] or "element"
            slug, n = base, 2
            while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)


class Technologie(models.Model):
    class Categorie(models.TextChoices):
        FRONTEND = "frontend", "Front-end"
        BACKEND = "backend", "Back-end"
        SYSTEME = "systeme", "Systèmes"
        RESEAU = "reseau", "Réseaux"
        SECURITE = "securite", "Sécurité"
        OUTIL = "outil", "Outils"

    nom = models.CharField(max_length=60, unique=True)
    icone = models.CharField(
        "icône",
        max_length=80,
        blank=True,
        help_text="Classe Devicon (ex. « devicon-python-plain ») ou Bootstrap Icons (ex. « bi-shield-lock »).",
    )
    categorie = models.CharField("catégorie", max_length=20, choices=Categorie.choices, default=Categorie.OUTIL)

    class Meta:
        ordering = ["categorie", "nom"]

    def __str__(self):
        return self.nom

    @property
    def icone_classe(self):
        if self.icone.startswith("bi-"):
            return f"bi {self.icone}"
        return f"{self.icone} colored" if self.icone else "bi bi-cpu"


class Projet(SlugMixin):
    titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="projets/", blank=True)
    technologies = models.ManyToManyField(Technologie, blank=True, related_name="projets")
    lien_github = models.URLField("lien GitHub", blank=True)
    lien_demo = models.URLField("lien démo", blank=True)
    date = models.DateField(default=timezone.localdate)
    a_la_une = models.BooleanField("à la une", default=False)

    class Meta:
        ordering = ["-a_la_une", "-date"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("portfolio:projet", args=[self.slug])

    def save(self, *args, **kwargs):
        reduire_image(self.image)
        super().save(*args, **kwargs)


class Competence(models.Model):
    class Categorie(models.TextChoices):
        SYSTEME = "systeme", "Systèmes & virtualisation"
        RESEAU = "reseau", "Réseaux & sécurité"
        WEB = "web", "Développement web"
        OUTIL = "outil", "Outils"
        SAVOIR_ETRE = "savoir_etre", "Savoir-être"
        LANGUE = "langue", "Langues"

    nom = models.CharField(max_length=100)
    niveau = models.PositiveSmallIntegerField(
        default=70, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="De 0 à 100."
    )
    categorie = models.CharField("catégorie", max_length=20, choices=Categorie.choices)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["categorie", "ordre", "-niveau"]
        verbose_name = "compétence"

    def __str__(self):
        return self.nom


class Experience(models.Model):
    class Type(models.TextChoices):
        PRO = "pro", "Expérience professionnelle"
        FORMATION = "formation", "Formation"
        CERTIFICATION = "certification", "Certification"

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.PRO)
    poste = models.CharField("poste / diplôme", max_length=150)
    organisation = models.CharField("entreprise / école", max_length=150)
    lieu = models.CharField(max_length=100, blank=True)
    date_debut = models.DateField("date de début")
    date_fin = models.DateField("date de fin", null=True, blank=True, help_text="Laisser vide si en cours.")
    description = models.TextField(blank=True, help_text="Une mission par ligne.")
    lien = models.URLField("lien de vérification", blank=True, help_text="Page publique qui atteste la certification.")

    class Meta:
        # Postes en cours d'abord, puis du plus récent au plus ancien.
        ordering = [models.F("date_fin").desc(nulls_first=True), "-date_debut"]
        verbose_name = "expérience"

    def __str__(self):
        return f"{self.poste} — {self.organisation}"

    @property
    def en_cours(self):
        return self.date_fin is None

    @property
    def missions(self):
        return [ligne.strip(" -•\t") for ligne in self.description.splitlines() if ligne.strip()]


class Formation(Experience):
    """Vue « formations » des entrées de parcours (même table, type = formation)."""

    class Meta:
        proxy = True
        verbose_name = "formation"


class Certification(Experience):
    """Vue « certifications » des entrées de parcours (même table, type = certification)."""

    class Meta:
        proxy = True
        verbose_name = "certification"


class Message(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField("e-mail")
    sujet = models.CharField(max_length=150)
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ["lu", "-date"]

    def __str__(self):
        return f"{self.nom} — {self.sujet}"


class ArticleQuerySet(models.QuerySet):
    def publies(self):
        return self.filter(publie=True, date_publication__lte=timezone.now())


class Article(SlugMixin):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to="articles/", blank=True)
    date_publication = models.DateTimeField("date de publication", default=timezone.now)
    publie = models.BooleanField("publié", default=False)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("portfolio:article", args=[self.slug])

    def save(self, *args, **kwargs):
        reduire_image(self.image)
        super().save(*args, **kwargs)
