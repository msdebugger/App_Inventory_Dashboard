from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Application, Category


class InventoryWriteAccessTests(TestCase):
    def test_anonymous_users_cannot_open_write_forms(self):
        write_urls = [
            reverse("application-add"),
            reverse("application-edit", kwargs={"slug": "existing-app"}),
            reverse("application-delete", kwargs={"slug": "existing-app"}),
            reverse("deployment-add", kwargs={"slug": "existing-app"}),
            reverse("license-add", kwargs={"slug": "existing-app"}),
        ]

        for url in write_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_existing_database_user_can_open_application_form(self):
        user_model = get_user_model()
        user_model.objects.create_user(username="inventory-user", password="test-password")
        self.assertTrue(self.client.login(username="inventory-user", password="test-password"))

        response = self.client.get(reverse("application-add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="themed-form"')
        self.assertContains(response, "Register a new application")
        self.assertContains(response, "Register application")

    def test_anonymous_users_cannot_write_through_api(self):
        response = APIClient().post("/api/applications/", data={}, format="json")

        self.assertIn(response.status_code, (401, 403))

    def test_login_and_related_forms_use_shared_theme_styles(self):
        category = Category.objects.create(name="Testing")
        application = Application.objects.create(name="Test application", category=category)
        user_model = get_user_model()
        user_model.objects.create_user(username="inventory-user", password="test-password")
        self.client.login(username="inventory-user", password="test-password")

        for url in (
            reverse("deployment-add", kwargs={"slug": application.slug}),
            reverse("license-add", kwargs={"slug": application.slug}),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="themed-form"')

        self.client.logout()
        login_response = self.client.get(reverse("login"))
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, 'class="themed-form"')
