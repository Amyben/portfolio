import base64

from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def email_protege(email, icone_seule=False):
    """Lien e-mail illisible pour les robots qui récoltent les adresses.

    L'adresse n'apparaît pas en clair dans le HTML : elle est inversée puis
    encodée en base64, et static/js/main.js la reconstitue dans le navigateur.
    Sans JavaScript, le lien mène au formulaire de contact.
    """
    code = base64.b64encode(email[::-1].encode()).decode()
    if icone_seule:
        return format_html(
            '<a class="js-email" data-e="{}" href="{}" aria-label="E-mail"><i class="bi bi-envelope"></i></a>',
            code, reverse("portfolio:contact"),
        )
    return format_html(
        '<a class="js-email" data-e="{}" data-texte href="{}">Écrire via le formulaire</a>',
        code, reverse("portfolio:contact"),
    )

