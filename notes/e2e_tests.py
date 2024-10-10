import logging
import time

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.cache import cache
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO)


class SecretNotesE2ETests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    def setUp(self):
        super().setUp()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def wait_for_element(self, by, value, timeout=20):
        try:
            element = WebDriverWait(self.selenium, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logging.info(f"Found element: {by}={value}")
            return element
        except Exception as e:
            logging.error(f"Failed to find element {by}={value}: {str(e)}")
            logging.error(f"Current URL: {self.selenium.current_url}")
            logging.error(f"Page source: {self.selenium.page_source}")
            raise

    def check_for_rate_limit(self):
        if "Rate Limit Exceeded" in self.selenium.page_source:
            logging.warning(
                "Rate limit exceeded. Waiting for 60 seconds before retrying."
            )
            time.sleep(60)
            self.selenium.refresh()

    def test_register_login_create_view_note(self):
        logging.info("Starting test_register_login_create_view_note")

        self.selenium.get(f"{self.live_server_url}{reverse('register')}")
        logging.info(f"Navigated to registration page: {self.selenium.current_url}")

        self.wait_for_element(By.NAME, "username").send_keys("testuser")
        self.wait_for_element(By.NAME, "password1").send_keys("testpassword123")
        self.wait_for_element(By.NAME, "password2").send_keys("testpassword123")
        self.wait_for_element(By.XPATH, "//button[text()='Register']").click()
        logging.info("Submitted registration form")

        self.wait_for_element(By.XPATH, "//span[contains(text(), 'Hello, testuser!')]")
        logging.info("Registration successful")

        self.selenium.get(f"{self.live_server_url}{reverse('create_note')}")
        logging.info(f"Navigated to create note page: {self.selenium.current_url}")

        self.check_for_rate_limit()

        content_input = self.wait_for_element(By.ID, "id_content")
        content_input.send_keys("This is a test secret note")

        max_views_input = self.wait_for_element(By.NAME, "max_views")
        max_views_input.clear()
        max_views_input.send_keys("2")

        expiration_hours_input = self.wait_for_element(By.NAME, "expiration_hours")
        expiration_hours_input.send_keys("24")

        self.wait_for_element(By.XPATH, "//button[text()='Create Note']").click()

        self.check_for_rate_limit()

        note_url = self.wait_for_element(
            By.XPATH, "//a[contains(@href, '/note/')]"
        ).get_attribute("href")

        self.selenium.get(self.live_server_url)
        self.wait_for_element(By.XPATH, "//button[contains(text(), 'Logout')]").click()

        for _ in range(2):
            self.selenium.get(note_url)
            note_content = self.wait_for_element(By.TAG_NAME, "p").text
            self.assertEqual(note_content, "This is a test secret note")

        self.selenium.get(note_url)
        error_message = self.wait_for_element(By.TAG_NAME, "h1").text
        self.assertEqual(error_message, "404 - Page Not Found")

    def test_view_nonexistent_note(self):
        self.selenium.get(
            f"{self.live_server_url}{reverse('view_note', kwargs={'url_key': '00000000-0000-0000-0000-000000000000'})}"
        )
        error_message = self.wait_for_element(By.TAG_NAME, "h1").text
        self.assertEqual(error_message, "404 - Page Not Found")

    def test_rate_limit(self):
        User.objects.create_user(username="testuser", password="12345")

        self.selenium.get(f"{self.live_server_url}{reverse('login')}")
        self.wait_for_element(By.NAME, "username").send_keys("testuser")
        self.wait_for_element(By.NAME, "password").send_keys("12345")
        self.wait_for_element(By.XPATH, "//button[text()='Login']").click()

        for i in range(16):
            self.selenium.get(f"{self.live_server_url}{reverse('create_note')}")
            logging.info(f"Attempt {i+1} to access create note page")
            if "Rate Limit Exceeded" in self.selenium.page_source:
                logging.info("Rate limit exceeded as expected")
                break
            time.sleep(0.1)

        error_message = self.wait_for_element(By.TAG_NAME, "h1").text
        self.assertEqual(error_message, "Rate Limit Exceeded")
