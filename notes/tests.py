from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .form import SecretNoteForm
from .models import SecretNote


class SecretNoteModelTest(TestCase):
    def test_is_expired(self):
        expired_note = SecretNote.objects.create(
            content="Expired note",
            expiration_time=timezone.now() - timezone.timedelta(hours=1),
        )
        self.assertTrue(expired_note.is_expired())

        max_views_note = SecretNote.objects.create(
            content="Max views note", max_views=1, views=1
        )
        self.assertTrue(max_views_note.is_expired())

        valid_note = SecretNote.objects.create(
            content="Valid note",
            expiration_time=timezone.now() + timezone.timedelta(hours=1),
        )
        self.assertFalse(valid_note.is_expired())


class SecretNoteFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"content": "Test note", "max_views": 5, "expiration_hours": 24}
        form = SecretNoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"content": "", "max_views": 0, "expiration_hours": 100}
        form = SecretNoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
