from django.contrib.auth.models import User
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

    def test_increment_view(self):
        note = SecretNote.objects.create(content="Test note", max_views=2)
        self.assertEqual(note.views, 0)
        note.increment_view()
        self.assertEqual(note.views, 1)
        note.increment_view()
        self.assertEqual(note.views, 2)
        self.assertTrue(note.is_expired())


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


class NoteCreationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_create_note_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("create_note"),
            {"content": "Test note content", "max_views": 3, "expiration_hours": 24},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Secret Note has been created")
        self.assertEqual(SecretNote.objects.count(), 1)

    def test_create_note_unauthenticated(self):
        response = self.client.post(
            reverse("create_note"),
            {"content": "Test note content", "max_views": 3, "expiration_hours": 24},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SecretNote.objects.count(), 0)


class NoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.note = SecretNote.objects.create(content="Test note content", max_views=2)

    def test_view_note(self):
        response = self.client.get(reverse("view_note", args=[self.note.url_key]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test note content")

        response = self.client.get(reverse("view_note", args=[self.note.url_key]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This note has now been deleted")
        self.assertEqual(SecretNote.objects.count(), 0)

    def test_view_expired_note(self):
        expired_note = SecretNote.objects.create(
            content="Expired note",
            expiration_time=timezone.now() - timezone.timedelta(hours=1),
        )
        response = self.client.get(reverse("view_note", args=[expired_note.url_key]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Note Expired")
        self.assertEqual(SecretNote.objects.count(), 1)


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a New Note")

    def test_index_view_with_url_key(self):
        note = SecretNote.objects.create(content="Test note content")
        response = self.client.get(reverse("index") + f"?url_key={note.url_key}")
        self.assertRedirects(response, reverse("view_note", args=[note.url_key]))


class UserAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_user_registration(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "password1": "testpass123",
                "password2": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "12345",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_user_logout(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("create_note"))
        self.assertEqual(response.status_code, 302)
