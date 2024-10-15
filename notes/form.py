from django import forms

from .models import SecretNote


class SecretNoteForm(forms.ModelForm):
    expiration_hours = forms.IntegerField(
        min_value=1,
        max_value=72,
        required=False,
    )

    class Meta:
        model = SecretNote
        fields = ["content", "max_views"]
        widgets = {"content": forms.Textarea()}
