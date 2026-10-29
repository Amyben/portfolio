from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, Experience, Message, Projet


class PagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("charger_cv", verbosity=0)

    def test_accueil_affiche_le_cv(self):
        r = self.client.get(reverse("portfolio:accueil"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "AFG Assurances")
        self.assertContains(r, "Google Cybersecurity")
        self.assertContains(r, "Serveur proxy pfSense")

    def test_charger_cv_est_idempotent(self):
        avant = Projet.objects.count()
        call_command("charger_cv", verbosity=0)
        self.assertEqual(Projet.objects.count(), avant)

    def test_liste_et_detail_projet(self):
        projet = Projet.objects.first()
        self.assertTrue(projet.slug)
        self.assertEqual(self.client.get(reverse("portfolio:projets")).status_code, 200)
        self.assertContains(self.client.get(reverse("portfolio:projets"), {"techno": "PHP"}), "gestion des stagiaires")
        self.assertEqual(self.client.get(projet.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(reverse("portfolio:projet", args=["inexistant"])).status_code, 404)

    def test_sans_projet_la_section_est_masquee(self):
        Projet.objects.all().delete()
        r = self.client.get(reverse("portfolio:accueil"))
        self.assertNotContains(r, "Projets à la une")
        self.assertNotContains(r, reverse("portfolio:projets"))

    def test_slug_unique(self):
        a = Projet.objects.create(titre="Même titre", description="x")
        b = Projet.objects.create(titre="Même titre", description="y")
        self.assertNotEqual(a.slug, b.slug)


class BlogTests(TestCase):
    def test_seuls_les_articles_publies_sont_visibles(self):
        pub = Article.objects.create(titre="Publié", contenu="ok", publie=True)
        brouillon = Article.objects.create(titre="Brouillon", contenu="non", publie=False)
        futur = Article.objects.create(
            titre="Futur", contenu="plus tard", publie=True,
            date_publication=timezone.now() + timezone.timedelta(days=2),
        )
        r = self.client.get(reverse("portfolio:blog"))
        self.assertContains(r, "Publié")
        self.assertNotContains(r, "Brouillon")
        self.assertEqual(self.client.get(pub.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(brouillon.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(futur.get_absolute_url()).status_code, 404)


class ContactTests(TestCase):
    data = {"nom": "Ada", "email": "ada@example.com", "sujet": "Mission", "contenu": "Bonjour"}

    def test_message_enregistre(self):
        r = self.client.post(reverse("portfolio:contact"), self.data, follow=True)
        self.assertContains(r, "bien été envoyé")
        msg = Message.objects.get()
        self.assertFalse(msg.lu)

    def test_honeypot_ignore_les_robots(self):
        self.client.post(reverse("portfolio:contact"), {**self.data, "site_web": "spam.example"})
        self.assertEqual(Message.objects.count(), 0)

    def test_formulaire_invalide(self):
        r = self.client.post(reverse("portfolio:contact"), {**self.data, "email": "pas-un-email"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Message.objects.count(), 0)

    @override_settings(CONTACT_NOTIFY_EMAIL="moi@example.com")
    def test_notification_email(self):
        from django.core import mail

        self.client.post(reverse("portfolio:contact"), self.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Mission", mail.outbox[0].subject)


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        call_command("charger_cv", verbosity=0)
        cls.admin = get_user_model().objects.create_superuser("admin", "admin@example.com", "motdepasse-test")
        Message.objects.create(nom="Ada", email="ada@example.com", sujet="Mission", contenu="Bonjour")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_tableau_de_bord(self):
        r = self.client.get(reverse("admin:index"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "1 message attend votre réponse")
        self.assertContains(r, "Serveur proxy pfSense")

    def test_pages_admin(self):
        projet = Projet.objects.first()
        for nom in ("projet", "technologie", "competence", "experience", "formation", "certification", "message", "article"):
            self.assertEqual(self.client.get(reverse(f"admin:portfolio_{nom}_changelist")).status_code, 200, nom)
            if nom != "message":
                self.assertEqual(self.client.get(reverse(f"admin:portfolio_{nom}_add")).status_code, 200, nom)
        for url in (
            reverse("admin:portfolio_projet_add"),
            reverse("admin:portfolio_projet_change", args=[projet.pk]),
            reverse("admin:auth_user_changelist"),
            reverse("admin:auth_user_change", args=[self.admin.pk]),
        ):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_chaque_section_de_parcours_ne_montre_que_son_type(self):
        experiences = self.client.get(reverse("admin:portfolio_experience_changelist")).content.decode()
        formations = self.client.get(reverse("admin:portfolio_formation_changelist")).content.decode()
        self.assertIn("AFG Assurances", experiences)
        self.assertNotIn("Baccalauréat", experiences)
        self.assertIn("Baccalauréat", formations)
        self.assertNotIn("AFG Assurances", formations)

    def test_ajouter_une_formation_depuis_l_admin(self):
        r = self.client.post(reverse("admin:portfolio_formation_add"), {
            "poste": "Master Cybersécurité", "organisation": "Université d'Abomey-Calavi", "lieu": "",
            "date_debut": "2026-10-01", "date_fin": "",
        })
        self.assertEqual(r.status_code, 302)
        f = Experience.objects.get(poste="Master Cybersécurité")
        self.assertEqual(f.type, Experience.Type.FORMATION)
        accueil = self.client.get(reverse("portfolio:accueil")).content.decode()
        self.assertIn("Master Cybersécurité", accueil)

    def test_ajouter_une_competence_depuis_l_admin(self):
        r = self.client.post(reverse("admin:portfolio_competence_add"), {
            "nom": "Analyse de logs", "niveau": 60, "categorie": "reseau", "ordre": 0,
        })
        self.assertEqual(r.status_code, 302)
        self.assertContains(self.client.get(reverse("portfolio:accueil")), "Analyse de logs")

    def test_ouvrir_un_message_le_marque_lu(self):
        msg = Message.objects.get()
        self.client.get(reverse("admin:portfolio_message_change", args=[msg.pk]))
        msg.refresh_from_db()
        self.assertTrue(msg.lu)

    def test_connexion_anonyme(self):
        self.client.logout()
        r = self.client.get(reverse("admin:login"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "admin-login.svg")


class EmailProtegeTests(TestCase):
    def test_adresse_absente_du_html_mais_encodee(self):
        import base64

        from django.conf import settings

        portfolio = {**settings.PORTFOLIO, "email": "moi@example.com"}
        with self.settings(PORTFOLIO=portfolio):
            for url in (reverse("portfolio:accueil"), reverse("portfolio:contact")):
                html = self.client.get(url).content.decode()
                self.assertNotIn("moi@example.com", html, url)
                self.assertIn(base64.b64encode(b"moc.elpmaxe@iom").decode(), html, url)
