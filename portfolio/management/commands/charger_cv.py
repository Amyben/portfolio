"""
Charge le contenu du CV (expériences, formations, compétences, technologies,
premiers projets). La commande est idempotente : on peut la relancer sans
créer de doublons. Les niveaux de compétences sont indicatifs, à ajuster
dans l'admin.

    python manage.py charger_cv
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from portfolio.models import Competence, Experience, Projet, Technologie

T = Technologie.Categorie
TECHNOLOGIES = [
    ("HTML5", "devicon-html5-plain", T.FRONTEND),
    ("CSS3", "devicon-css3-plain", T.FRONTEND),
    ("Bootstrap", "devicon-bootstrap-plain", T.FRONTEND),
    ("JavaScript", "devicon-javascript-plain", T.FRONTEND),
    ("PHP", "devicon-php-plain", T.BACKEND),
    ("Python", "devicon-python-plain", T.BACKEND),
    ("Django", "devicon-django-plain", T.BACKEND),
    ("Linux", "devicon-linux-plain", T.SYSTEME),
    ("Windows Server", "bi-windows", T.SYSTEME),
    ("VMware", "bi-hdd-stack", T.SYSTEME),
    ("VirtualBox", "bi-boxes", T.SYSTEME),
    ("GNS3", "bi-diagram-3", T.RESEAU),
    ("Cisco Packet Tracer", "bi-router", T.RESEAU),
    ("pfSense", "bi-shield-lock", T.SECURITE),
    ("Wireshark", "bi-activity", T.SECURITE),
    ("Nmap", "bi-radar", T.SECURITE),
    ("GLPI", "bi-ticket-detailed", T.OUTIL),
    ("Photoshop", "devicon-photoshop-plain", T.OUTIL),
]

C = Competence.Categorie
COMPETENCES = [
    ("Administration Windows Server", 75, C.SYSTEME),
    ("Administration Linux", 70, C.SYSTEME),
    ("Virtualisation (VMware, VirtualBox)", 75, C.SYSTEME),
    ("Maintenance matériel & logiciel", 90, C.SYSTEME),
    ("Réseaux (GNS3, Cisco Packet Tracer)", 75, C.RESEAU),
    ("Câblage & imprimantes réseau", 85, C.RESEAU),
    ("Sécurité réseau (Wireshark, Nmap, pfSense)", 70, C.RESEAU),
    ("HTML5 / CSS3 / Bootstrap", 85, C.WEB),
    ("JavaScript", 70, C.WEB),
    ("PHP", 70, C.WEB),
    ("Python / Django", 65, C.WEB),
    ("GLPI", 70, C.OUTIL),
    ("Adobe Photoshop", 60, C.OUTIL),
    ("Rigueur et sens du détail", 90, C.SAVOIR_ETRE),
    ("Polyvalence technique", 90, C.SAVOIR_ETRE),
    ("Pédagogie et écoute", 90, C.SAVOIR_ETRE),
    ("Autonomie et gestion du temps", 85, C.SAVOIR_ETRE),
    ("Français — courant", 90, C.LANGUE),
    ("Fon — langue maternelle", 100, C.LANGUE),
    ("Anglais — débutant", 30, C.LANGUE),
]

E = Experience.Type
EXPERIENCES = [
    (E.PRO, "Technicien de maintenance informatique", "LES 2BL DOCUPRINT", "Bohicon",
     date(2025, 9, 1), None,
     "Assurer la maintenance des équipements matériels et logiciels du centre de formation.\n"
     "Diagnostiquer et résoudre les problèmes informatiques rencontrés par les apprenants et le centre."),
    (E.PRO, "Stagiaire Support IT", "AFG Assurances", "Cotonou",
     date(2025, 10, 1), date(2026, 3, 31),
     "Installer et configurer les postes utilisateurs ainsi que les imprimantes réseau (impression et numérisation).\n"
     "Diagnostiquer les pannes courantes et assurer la maintenance préventive des équipements.\n"
     "Réaliser le câblage réseau et l'assistance aux utilisateurs."),
    (E.PRO, "Encadreur / Formateur en Développement Web", "Institut des Multimédias Appliqués", "Bohicon",
     date(2025, 4, 1), date(2025, 10, 31),
     "Former des apprenants débutants en HTML5, CSS3, Bootstrap, JavaScript et PHP.\n"
     "Concevoir et animer des séances pédagogiques adaptées, avec suivi individualisé de la progression."),
    (E.PRO, "Technicien Informatique", "CFAIJ-ONG", "Bohicon",
     date(2024, 6, 1), date(2025, 8, 31),
     "Former les apprenants en maintenance informatique et réseaux.\n"
     "Installer, configurer et dépanner les équipements matériels et logiciels."),
    (E.PRO, "Stagiaire Administrateur Réseaux et Systèmes", "2CL Services", "Bohicon",
     date(2024, 2, 1), date(2024, 5, 31),
     "Mettre en place un serveur proxy pfSense et superviser la maintenance préventive des infrastructures réseaux."),
    (E.PRO, "Stagiaire Développeur Web", "2CL Services", "Bohicon",
     date(2023, 7, 1), date(2023, 9, 30),
     "Développer une application web de gestion des stagiaires (HTML5, CSS3, Bootstrap, JavaScript, PHP)."),
    (E.FORMATION, "Licence Professionnelle en Sécurité des Systèmes et Réseaux Informatiques",
     "Institut Universitaire Les Cours Sonou", "", date(2024, 1, 1), date(2024, 12, 31), ""),
    (E.FORMATION, "Baccalauréat Série D", "CEG Avogbanna", "", date(2018, 1, 1), date(2018, 12, 31), ""),
    (E.CERTIFICATION, "Google Cybersecurity Professional Certificate", "Coursera", "",
     date(2024, 1, 1), date(2024, 12, 31), ""),
]

PROJETS = [
    {
        "titre": "Application de gestion des stagiaires",
        "date": date(2023, 9, 30),
        "description": (
            "Application web de gestion des stagiaires développée lors de mon stage chez 2CL Services "
            "(juillet – septembre 2023).\n\n"
            "Réalisée en HTML5, CSS3, Bootstrap, JavaScript et PHP. Description à compléter dans l'admin."
        ),
        "technologies": ["HTML5", "CSS3", "Bootstrap", "JavaScript", "PHP"],
    },
    {
        "titre": "Serveur proxy pfSense",
        "date": date(2024, 5, 31),
        "description": (
            "Mise en place d'un serveur proxy pfSense lors de mon stage d'administrateur réseaux et "
            "systèmes chez 2CL Services, avec supervision de la maintenance préventive des "
            "infrastructures réseaux. Description à compléter dans l'admin."
        ),
        "technologies": ["pfSense"],
    },
]


class Command(BaseCommand):
    help = "Charge les données du CV dans la base (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        for nom, icone, cat in TECHNOLOGIES:
            Technologie.objects.update_or_create(nom=nom, defaults={"icone": icone, "categorie": cat})

        for ordre, (nom, niveau, cat) in enumerate(COMPETENCES):
            Competence.objects.update_or_create(
                nom=nom, categorie=cat, defaults={"niveau": niveau, "ordre": ordre}
            )

        for type_, poste, org, lieu, debut, fin, desc in EXPERIENCES:
            Experience.objects.update_or_create(
                poste=poste, organisation=org,
                defaults={"type": type_, "lieu": lieu, "date_debut": debut, "date_fin": fin, "description": desc},
            )

        for data in PROJETS:
            data = dict(data)
            technos = data.pop("technologies")
            projet, _ = Projet.objects.get_or_create(titre=data["titre"], defaults={**data, "a_la_une": True})
            projet.technologies.set(Technologie.objects.filter(nom__in=technos))

        if options["verbosity"]:
            self.stdout.write(self.style.SUCCESS(
                f"CV chargé : {Technologie.objects.count()} technologies, {Competence.objects.count()} compétences, "
                f"{Experience.objects.count()} expériences/formations, {Projet.objects.count()} projets."
            ))
