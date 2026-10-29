# forpo — Portfolio Django

Portfolio personnel (projets, compétences, parcours, blog, contact) avec une interface d'administration pour gérer le contenu. Conçu pour être hébergé sur **PythonAnywhere**.

- Django 5.2 (LTS) · Python 3.10 à 3.13
- SQLite par défaut (MySQL en option)
- Dépendances : Django, django-unfold (thème de l'admin), Pillow, python-dotenv
- Admin : thème [Unfold](https://unfoldadmin.com) en mode sombre « console », tableau de bord personnalisé (`templates/admin/index.html`, `portfolio/dashboard.py`), configuration dans `UNFOLD` (`config/settings.py`)

## Modèles

| Modèle | Champs |
|---|---|
| Projet | titre, slug, description, image, technologies, lien GitHub, lien démo, date, à la une |
| Technologie | nom, icône (classe Devicon ou Bootstrap Icons), catégorie |
| Competence | nom, niveau (0–100), catégorie, ordre |
| Experience | type (pro / formation / certification), poste, entreprise/école, lieu, date début, date fin (vide = en cours), description (une mission par ligne) |
| Message | nom, e-mail, sujet, contenu, date, lu/non lu |
| Article | titre, slug, contenu, image, date de publication, publié |

Les images envoyées sont automatiquement redimensionnées (1600 px max, JPEG) pour économiser le disque (512 Mo sur le compte gratuit).

## En local

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env          # puis DEBUG=True, ALLOWED_HOSTS=localhost,127.0.0.1, ADMIN_URL=admin/
./venv/bin/python manage.py migrate
./venv/bin/python manage.py charger_cv        # importe le CV (relançable sans doublons)
./venv/bin/python manage.py createsuperuser
./venv/bin/python manage.py runserver
```

Site : http://127.0.0.1:8000 · Admin : http://127.0.0.1:8000/admin/ · Tests : `./venv/bin/python manage.py test portfolio`

## Déploiement sur PythonAnywhere

Remplacer `votrecompte` par votre nom d'utilisateur PythonAnywhere.

1. **Envoyer le code** dans `/home/votrecompte/forpo` : via GitHub (`git clone` dans une console Bash) ou en téléversant une archive dans l'onglet *Files*. Ne pas envoyer `venv/`, `db.sqlite3` ni `.env`.

2. **Environnement virtuel** (console Bash) :
   ```bash
   cd ~/forpo
   mkvirtualenv --python=python3.12 forpo
   pip install -r requirements.txt
   ```

3. **Fichier `.env`** :
   ```bash
   cp .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
   nano .env    # SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=votrecompte.pythonanywhere.com, ADMIN_URL, PORTFOLIO_*
   ```

4. **Base, données, statiques** :
   ```bash
   python manage.py migrate
   python manage.py charger_cv
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

5. **Onglet Web** → *Add a new web app* → **Manual configuration** (pas « Django ») → Python 3.12.
   - *Virtualenv* : `/home/votrecompte/.virtualenvs/forpo`
   - *WSGI configuration file* : remplacer tout le contenu par celui de `pythonanywhere_wsgi.py` (en adaptant le chemin).
   - *Static files* :

     | URL | Directory |
     |---|---|
     | `/static/` | `/home/votrecompte/forpo/staticfiles` |
     | `/media/` | `/home/votrecompte/forpo/media` |

   - *Security* : activer **Force HTTPS**.
   - Cliquer sur **Reload**.

6. **Mises à jour** ultérieures : `git pull`, puis `pip install -r requirements.txt`, `python manage.py migrate`, `python manage.py collectstatic --noinput`, et **Reload** dans l'onglet Web.

### Points d'attention PythonAnywhere

- **Fichiers statiques et média** : servis par PythonAnywhere via les mappings ci-dessus, pas par Django (`DEBUG=False`). Après toute modification CSS/JS, relancer `collectstatic`.
- **Compte gratuit** : 512 Mo de disque, accès Internet sortant limité à une liste blanche. Les messages de contact sont toujours enregistrés en base (consultables dans l'admin). La notification par e-mail est optionnelle ; `smtp.gmail.com` est autorisé (utiliser un *mot de passe d'application* Google).
- **Renouvellement** : sur le compte gratuit, l'application doit être prolongée tous les 3 mois (bouton *Run until 3 months from today* dans l'onglet Web).
- **Erreurs** : consulter l'*error log* et le *server log* depuis l'onglet Web.
- **URL de l'admin** : configurable via `ADMIN_URL` pour éviter les robots qui ciblent `/admin/`.
- **MySQL** (optionnel) : créer la base dans l'onglet *Databases*, puis `DB_ENGINE=mysql` et les variables `DB_*` dans `.env` (`mysqlclient` est préinstallé).

## Personnalisation

- Nom, titre, coordonnées, réseaux : variables `PORTFOLIO_*` dans `.env`.
- Texte « À propos » : `templates/portfolio/accueil.html`.
- Couleurs et polices : variables CSS en haut de `static/css/style.css` (mêmes teintes que l'admin).
- Scène 3D de l'en-tête : `static/js/scene.js` (Three.js chargé depuis le CDN jsDelivr par le navigateur, rien à installer sur le serveur). Sans WebGL, ou si le visiteur demande moins d'animations, la scène est fixe ou remplacée par `static/img/admin-login.svg`.
- Blog désactivable : `PORTFOLIO_BLOG=False`.
- Admin : couleurs, icônes du menu et visuel de connexion dans le dictionnaire `UNFOLD` de `config/settings.py` ; styles complémentaires dans `static/css/admin-futur.css`. Retirer `"THEME": "dark"` pour réactiver le choix clair/sombre.
- Traductions de l'admin : Unfold n'est pas traduit en français, ses textes le sont dans `locale/fr/LC_MESSAGES/django.po`. Après modification : `python scripts/compiler_traductions.py` (ou `python manage.py compilemessages` si gettext est installé).
