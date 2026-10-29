from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import Article, Certification, Competence, Experience, Formation, Message, Projet, Technologie

admin.site.index_title = "Tableau de bord"

# Utilisateurs et groupes ré-enregistrés avec les formulaires du thème Unfold.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class PortfolioAdmin(ModelAdmin):
    """Titre de liste lisible (« Projets ») au lieu de « Sélectionnez l'objet projet à changer »."""

    warn_unsaved_form = True

    def changelist_view(self, request, extra_context=None):
        extra_context = {"title": self.opts.verbose_name_plural.capitalize(), **(extra_context or {})}
        return super().changelist_view(request, extra_context)


@admin.register(Technologie)
class TechnologieAdmin(PortfolioAdmin):
    list_display = ("nom", "afficher_categorie", "icone")
    list_filter = ("categorie",)
    search_fields = ("nom",)

    @display(description="Catégorie", ordering="categorie", label=True)
    def afficher_categorie(self, obj):
        return obj.get_categorie_display()


@admin.register(Projet)
class ProjetAdmin(PortfolioAdmin):
    list_display = ("apercu", "titre", "date", "a_la_une")
    list_display_links = ("apercu", "titre")
    list_editable = ("a_la_une",)
    list_filter = ("a_la_une", "technologies")
    search_fields = ("titre", "description")
    prepopulated_fields = {"slug": ("titre",)}
    filter_horizontal = ("technologies",)
    date_hierarchy = "date"

    @display(description="Aperçu", image=True)
    def apercu(self, obj):
        return obj.image.url if obj.image else None


@admin.register(Competence)
class CompetenceAdmin(PortfolioAdmin):
    list_display = ("nom", "afficher_categorie", "niveau", "ordre")
    list_editable = ("niveau", "ordre")
    list_filter = ("categorie",)
    search_fields = ("nom",)

    @display(description="Catégorie", ordering="categorie", label=True)
    def afficher_categorie(self, obj):
        return obj.get_categorie_display()


class ParcoursAdmin(PortfolioAdmin):
    """Base des sections Expériences, Formations et Certifications.

    Les trois partagent la table Experience : chaque section ne montre que son
    type, le renseigne automatiquement et adapte les libellés du formulaire.
    """

    type_parcours = None
    libelles = {}
    list_display = ("poste", "organisation", "date_debut", "date_fin")
    search_fields = ("poste", "organisation", "description")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(type=self.type_parcours)

    def __init_subclass__(cls, **kwargs):
        # Les en-têtes de colonnes reprennent les libellés propres à la section.
        super().__init_subclass__(**kwargs)
        colonnes = []
        for champ in cls.list_display:
            if champ in cls.libelles:
                colonne = display(description=cls.libelles[champ], ordering=champ)(
                    lambda self, obj, champ=champ: getattr(obj, champ)
                )
                setattr(cls, f"col_{champ}", colonne)
                champ = f"col_{champ}"
            colonnes.append(champ)
        cls.list_display = tuple(colonnes)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for champ, libelle in self.libelles.items():
            if champ in form.base_fields:
                form.base_fields[champ].label = libelle
        return form

    def save_model(self, request, obj, form, change):
        obj.type = self.type_parcours
        super().save_model(request, obj, form, change)


@admin.register(Experience)
class ExperienceAdmin(ParcoursAdmin):
    type_parcours = Experience.Type.PRO
    fields = ("poste", "organisation", "lieu", "date_debut", "date_fin", "description")
    libelles = {"poste": "Poste", "organisation": "Entreprise", "description": "Missions"}
    list_display = ("poste", "organisation", "date_debut", "afficher_fin")

    @display(description="Fin", ordering="date_fin", label={"En cours": "info"})
    def afficher_fin(self, obj):
        return "En cours" if obj.en_cours else obj.date_fin.strftime("%d/%m/%Y")


@admin.register(Formation)
class FormationAdmin(ParcoursAdmin):
    type_parcours = Experience.Type.FORMATION
    fields = ("poste", "organisation", "lieu", "date_debut", "date_fin")
    libelles = {
        "poste": "Diplôme",
        "organisation": "École / établissement",
        "date_debut": "Début de la formation",
        "date_fin": "Date d'obtention",
    }


@admin.register(Certification)
class CertificationAdmin(ParcoursAdmin):
    type_parcours = Experience.Type.CERTIFICATION
    fields = ("poste", "organisation", "date_debut", "lien")
    libelles = {"poste": "Certification", "organisation": "Organisme", "date_debut": "Date d'obtention"}
    list_display = ("poste", "organisation", "date_debut")


@admin.register(Message)
class MessageAdmin(PortfolioAdmin):
    list_display = ("sujet", "nom", "email", "date", "etat")
    list_filter = ("lu",)
    search_fields = ("nom", "email", "sujet", "contenu")
    readonly_fields = ("nom", "email", "sujet", "contenu", "date")
    actions = ("marquer_lu", "marquer_non_lu")
    warn_unsaved_form = False

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        Message.objects.filter(pk=object_id, lu=False).update(lu=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @display(description="État", ordering="lu", label={"Nouveau": "info", "Lu": "default"})
    def etat(self, obj):
        return "Lu" if obj.lu else "Nouveau"

    @action(description="Marquer comme lu")
    def marquer_lu(self, request, queryset):
        queryset.update(lu=True)

    @action(description="Marquer comme non lu")
    def marquer_non_lu(self, request, queryset):
        queryset.update(lu=False)


@admin.register(Article)
class ArticleAdmin(PortfolioAdmin):
    list_display = ("apercu", "titre", "date_publication", "publie")
    list_display_links = ("apercu", "titre")
    list_editable = ("publie",)
    list_filter = ("publie",)
    search_fields = ("titre", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_publication"

    @display(description="Aperçu", image=True)
    def apercu(self, obj):
        return obj.image.url if obj.image else None
