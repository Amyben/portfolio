from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("projets/", views.projets, name="projets"),
    path("projets/<slug:slug>/", views.projet, name="projet"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.article, name="article"),
    path("contact/", views.contact, name="contact"),
]
