from django import forms

from .models import Message


class ContactForm(forms.ModelForm):
    # Champ piège invisible : les robots le remplissent, pas les humains.
    site_web = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = Message
        fields = ("nom", "email", "sujet", "contenu")
        labels = {"contenu": "Message"}
        widgets = {
            "nom": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Votre nom"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "vous@exemple.com"}),
            "sujet": forms.TextInput(attrs={"placeholder": "Objet de votre message"}),
            "contenu": forms.Textarea(attrs={"rows": 6, "placeholder": "Bonjour…"}),
        }

    def est_spam(self):
        return bool(self.cleaned_data.get("site_web"))
