"""
Paramètres Django du portfolio « forpo ».

Toutes les valeurs sensibles ou propres à l'environnement sont lues dans un
fichier `.env` (voir `.env.example`). En production sur PythonAnywhere :
DEBUG=False, ALLOWED_HOSTS=<utilisateur>.pythonanywhere.com, et les fichiers
statiques/média sont servis par le serveur de PythonAnywhere (onglet « Web »,
section « Static files »).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [v.strip() for v in os.getenv(name, default).split(",") if v.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")]

INSTALLED_APPS = [
    "unfold",  # thème de l'admin, doit précéder django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portfolio.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de données : SQLite par défaut (suffisant pour un portfolio et
# disponible sur tous les comptes PythonAnywhere). MySQL est possible en
# définissant DB_ENGINE=mysql (mysqlclient est préinstallé sur PythonAnywhere).
if os.getenv("DB_ENGINE", "sqlite") == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "OPTIONS": {"charset": "utf8mb4", "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Porto-Novo"
USE_I18N = True
# Traductions françaises du thème Unfold (voir scripts/compiler_traductions.py).
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_TZ = True

# Fichiers statiques et média — à déclarer dans l'onglet Web de PythonAnywhere :
#   URL /static/  ->  <BASE_DIR>/staticfiles
#   URL /media/   ->  <BASE_DIR>/media
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Taille max des images envoyées (le compte gratuit dispose de 512 Mo de disque).
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "3"))
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_MB * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# E-mail : notification lors d'un nouveau message de contact (optionnelle).
# Les comptes gratuits PythonAnywhere ne peuvent joindre que des hôtes de la
# liste blanche ; smtp.gmail.com en fait partie (utiliser un mot de passe
# d'application Google).
if os.getenv("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
    EMAIL_TIMEOUT = 10
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", os.getenv("EMAIL_HOST_USER", "webmaster@localhost"))
CONTACT_NOTIFY_EMAIL = os.getenv("CONTACT_NOTIFY_EMAIL", "")

# Informations affichées sur le site (nom, titre, coordonnées).
PORTFOLIO = {
    "nom": os.getenv("PORTFOLIO_NOM", "Votre Nom"),
    "titre": os.getenv("PORTFOLIO_TITRE", "Technicien IT Support | Systèmes & Réseaux"),
    "accroche": os.getenv(
        "PORTFOLIO_ACCROCHE",
        "Bonjour, je suis technicien IT support, spécialisé en systèmes et réseaux.\n"
        "J’aide à installer, administrer et sécuriser les infrastructures informatiques, "
        "tout en développant des solutions web et en transmettant mes compétences techniques.",
    ),
    # Domaines affichés sous l'accroche : (libellé, icône Bootstrap Icons).
    "domaines": [
        ("Réseaux & systèmes", "bi-diagram-3"),
        ("Cybersécurité", "bi-shield-lock"),
        ("Développement web", "bi-code-slash"),
        ("Formation", "bi-mortarboard"),
    ],
    "ville": os.getenv("PORTFOLIO_VILLE", "Bénin"),
    "email": os.getenv("PORTFOLIO_EMAIL", ""),
    "telephone": os.getenv("PORTFOLIO_TELEPHONE", ""),
    "github": os.getenv("PORTFOLIO_GITHUB", ""),
    "linkedin": os.getenv("PORTFOLIO_LINKEDIN", ""),
    "blog_actif": env_bool("PORTFOLIO_BLOG", True),
}

if not DEBUG:
    # PythonAnywhere termine le HTTPS devant l'application.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}

# ---------------------------------------------------------------------------
# Admin : thème Unfold, direction « console futuriste » (sombre, bleu ionique).
# ---------------------------------------------------------------------------
from django.templatetags.static import static  # noqa: E402
from django.urls import reverse_lazy  # noqa: E402

UNFOLD = {
    "SITE_TITLE": "Portfolio",
    "SITE_HEADER": "Portfolio",
    "SITE_SUBHEADER": "Console d'administration",
    "SITE_SYMBOL": "hub",
    "SITE_URL": "/",
    "SITE_FAVICONS": [{"rel": "icon", "type": "image/svg+xml", "href": lambda request: static("img/favicon.svg")}],
    "THEME": "dark",
    "BORDER_RADIUS": "10px",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "portfolio.dashboard.dashboard_callback",
    "STYLES": [
        lambda request: "https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&display=swap",
        lambda request: static("css/admin-futur.css"),
    ],
    "LOGIN": {"image": lambda request: static("img/admin-login.svg")},
    "COLORS": {
        # Gris « espace » légèrement bleutés.
        "base": {
            "50": "oklch(98% .005 268)",
            "100": "oklch(96% .009 268)",
            "200": "oklch(91% .015 268)",
            "300": "oklch(84% .022 268)",
            "400": "oklch(70% .03 268)",
            "500": "oklch(56% .035 268)",
            "600": "oklch(45% .04 268)",
            "700": "oklch(34% .045 270)",
            "800": "oklch(25.5% .045 272)",
            "900": "oklch(19% .042 274)",
            "950": "oklch(14% .036 276)",
        },
        # Bleu ionique.
        "primary": {
            "50": "oklch(97% .02 240)",
            "100": "oklch(93.5% .045 240)",
            "200": "oklch(88% .08 242)",
            "300": "oklch(81% .13 244)",
            "400": "oklch(73% .17 248)",
            "500": "oklch(65% .2 252)",
            "600": "oklch(58% .215 258)",
            "700": "oklch(51% .2 262)",
            "800": "oklch(44% .17 264)",
            "900": "oklch(38% .14 266)",
            "950": "oklch(28% .1 268)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Pilotage",
                "items": [
                    {"title": "Tableau de bord", "icon": "space_dashboard", "link": reverse_lazy("admin:index")},
                    {
                        "title": "Messages",
                        "icon": "mail",
                        "link": reverse_lazy("admin:portfolio_message_changelist"),
                        "badge": "portfolio.dashboard.badge_messages",
                    },
                ],
            },
            {
                "title": "Contenu",
                "separator": True,
                "items": [
                    {"title": "Projets", "icon": "rocket_launch", "link": reverse_lazy("admin:portfolio_projet_changelist")},
                    {"title": "Technologies", "icon": "memory", "link": reverse_lazy("admin:portfolio_technologie_changelist")},
                    {"title": "Articles", "icon": "edit_note", "link": reverse_lazy("admin:portfolio_article_changelist")},
                ],
            },
            {
                "title": "Parcours",
                "separator": True,
                "items": [
                    {"title": "Expériences", "icon": "work", "link": reverse_lazy("admin:portfolio_experience_changelist")},
                    {"title": "Formations", "icon": "school", "link": reverse_lazy("admin:portfolio_formation_changelist")},
                    {"title": "Certifications", "icon": "workspace_premium", "link": reverse_lazy("admin:portfolio_certification_changelist")},
                    {"title": "Compétences", "icon": "bolt", "link": reverse_lazy("admin:portfolio_competence_changelist")},
                ],
            },
            {
                "title": "Accès",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Utilisateurs",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Groupes",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
}
