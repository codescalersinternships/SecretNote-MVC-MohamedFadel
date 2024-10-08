from django.shortcuts import render
from django.utils import timezone

from .form import SecretNoteForm
from .models import SecretNote


def create_note(request):
    if request.method == "POST":
        form = SecretNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)

            if form.cleaned_data["expiration_hours"]:
                note.expiration_time = timezone.now() + timezone.timedelta(
                    hours=form.cleaned_data["expiration_hours"]
                )
            note.save()

            return render(request, "note_created.html", {"note": note})

    else:
        form = SecretNoteForm()
    return render(request, "create_note.html", {"form": form})
