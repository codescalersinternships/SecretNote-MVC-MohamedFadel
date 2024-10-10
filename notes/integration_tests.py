from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import SecretNote


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_create_and_view_note(self):
        create_url = reverse("create_note")
        create_data = {
            "content": "This is a test note",
            "max_views": 2,
            "expiration_hours": 24,
        }
        response = self.client.post(create_url, create_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Secret Note has been created")

        url_key = response.context["note"].url_key

        view_url = reverse("view_note", args=[url_key])
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a test note")

        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This note has now been deleted")

        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 404)

    def test_note_expiration(self):
        note = SecretNote.objects.create(
            content="This note will expire soon",
            user=self.user,
            expiration_time=timezone.now() + timezone.timedelta(hours=1),
        )

        view_url = reverse("view_note", args=[note.url_key])
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This note will expire soon")

        note.expiration_time = timezone.now() - timezone.timedelta(minutes=1)
        note.save()

        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "This note has expired or has already been viewed."
        )

    def test_user_flow(self):
        self.client.logout()

        register_url = reverse("register")
        register_data = {
            "username": "newuser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        response = self.client.post(register_url, register_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

        index_url = reverse("index")
        response = self.client.get(index_url)
        self.assertIn(response.status_code, [200, 429])

        if response.status_code == 429:
            self.assertContains(
                response,
                "You have exceeded the rate limit. Please try again later.",
                status_code=429,
            )
        else:
            self.assertContains(response, "Create a New Note")

        create_url = reverse("create_note")
        create_data = {
            "content": "Note created by new user",
            "max_views": 1,
            "expiration_hours": 24,
        }
        response = self.client.post(create_url, create_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Secret Note has been created")

        logout_url = reverse("logout")
        response = self.client.post(logout_url)
        self.assertIn(response.status_code, [200, 302])

        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('login')}?next={create_url}")

    def test_rate_limiting(self):
        view_url = reverse("index")

        for _ in range(5):
            response = self.client.get(view_url)
            self.assertEqual(response.status_code, 200)

        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 429)
        self.assertContains(
            response,
            "You have exceeded the rate limit. Please try again later.",
            status_code=429,
        )
