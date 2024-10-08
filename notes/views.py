from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from .form import SecretNoteForm
from .models import SecretNote


@ratelimit(key="ip", rate="5/m", method=["GET", "POST"], block=True)
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


@ratelimit(key="ip", rate="10/m", method=["GET"], block=True)
def view_note(request, url_key):
    note = get_object_or_404(SecretNote, url_key=url_key)
    if note.is_expired():
        note.delete()
        return render(request, "note_expired.html")

    note.increment_view()
    if note.is_expired():
        content = note.content
        note.delete()
        return render(request, "note_view.html", {"content": content, "deleted": True})

    return render(
        request, "note_view.html", {"content": note.content, "deleted": False}
    )


def ratelimit_error(request):
    return render(request, "ratelimit_error.html", status=429)
