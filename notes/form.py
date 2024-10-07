from django import forms

from .models import SecretNote


class SecretNoteForm(forms.ModelForm):
    expiration_hours = forms.IntegerField(
        min_value=1,
        max_value=72,
        required=False,
        help_text="Number of hours before the note expires",
    )

    class Meta:
        model = SecretNote
        fields = ["content", "max_views"]
        widgets = {"content": forms.Textarea(attrs={"rows": 4, "cols": 50})}
