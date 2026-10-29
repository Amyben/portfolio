# Modèle de fichier WSGI pour PythonAnywhere.
# Copier ce contenu dans /var/www/<votrecompte>_pythonanywhere_com_wsgi.py
# (onglet Web > « WSGI configuration file »), en remplaçant <votrecompte>.
import os
import sys

chemin = "/home/<votrecompte>/forpo"
if chemin not in sys.path:
    sys.path.insert(0, chemin)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
