from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from book_service.models import Book


class BookViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user1@example.com", password="securepassword"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": Book.Cover.HARD,
            "inventory": 10,
            "fee": 20,
        }

    def test_list_books(self):
        response = self.client.get("/api/book_service/books/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_book(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.get(f"/api/book_service/books/{book.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.book_data["title"])

    def test_create_book_unauthorized(self):
        response = self.client.post("/api/book_service/books/", self.book_data)
        self.assertEqual(response.status_code, 403)

    def test_create_book_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin_user).access_token}"
        )
        response = self.client.post("/api/book_service/books/", self.book_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], self.book_data["title"])

    def test_update_book_unauthorized(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.put(
            f"/api/book_service/books/{book.id}/", self.book_data
        )
        self.assertEqual(response.status_code, 403)

    def test_update_book_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin_user).access_token}"
        )
        book = Book.objects.create(**self.book_data)
        updated_data = {
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": Book.Cover.SOFT,
            "inventory": 15,
            "fee": 25,
        }
        response = self.client.put(f"/api/book_service/books/{book.id}/", updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], updated_data["title"])

    def test_partial_update_book_unauthorized(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.patch(
            f"/api/book_service/books/{book.id}/", {"title": "Partial Updated Book"}
        )
        self.assertEqual(response.status_code, 403)

    def test_partial_update_book_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin_user).access_token}"
        )
        book = Book.objects.create(**self.book_data)
        response = self.client.patch(
            f"/api/book_service/books/{book.id}/", {"title": "Partial Updated Book"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Partial Updated Book")

    def test_delete_book_unauthorized(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.delete(f"/api/book_service/books/{book.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_book_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin_user).access_token}"
        )
        book = Book.objects.create(**self.book_data)
        response = self.client.delete(f"/api/book_service/books/{book.id}/")
        self.assertEqual(response.status_code, 204)
