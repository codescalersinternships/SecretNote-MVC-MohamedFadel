from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from .form import SecretNoteForm
from .models import SecretNote


@ratelimit(key="ip", rate="15/m", method=["GET"])
def index(request):
    url_key = request.GET.get("url_key")
    if url_key:
        return redirect("view_note", url_key=url_key)

    return render(request, "index.html")


@login_required
@ratelimit(key="ip", rate="15/m", method=["GET", "POST"])
def create_note(request):
    if request.method == "POST":
        form = SecretNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user

            if form.cleaned_data["expiration_hours"]:
                note.expiration_time = timezone.now() + timezone.timedelta(
                    hours=form.cleaned_data["expiration_hours"]
                )
            note.save()

            return render(request, "note_created.html", {"note": note})

    else:
        form = SecretNoteForm()
    return render(request, "create_note.html", {"form": form})


@ratelimit(key="ip", rate="15/m", method=["GET"])
def view_note(request, url_key=None):
    if not url_key or url_key == "00000000-0000-0000-0000-000000000000":
        url_key = request.GET.get("url_key")
        if not url_key:
            return redirect("index")

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


def ratelimit_error(request, exception=None):
    return render(request, "ratelimit_error.html", status=429)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})
