from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from book_service.models import Book
from borrowing_service.models import BorrowingService
from datetime import datetime, timedelta


class BorrowingServiceViewSetTests(APITestCase):
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

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.Cover.HARD,
            inventory=10,
            fee=20,
        )

        self.borrowing_data = {
            "borrow_date": datetime.today().strftime("%Y-%m-%d"),
            "expected_return": (datetime.today() + timedelta(days=7)).strftime(
                "%Y-%m-%d"
            ),
            "book": self.book.id,
        }

    def test_list_borrowings(self):
        response = self.client.get("/api/borrowing_service/borrow/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    def test_create_borrowing(self):
        response = self.client.post(
            "/api/borrowing_service/borrow/", self.borrowing_data
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Book.objects.get(id=response.data["book"]).title, self.book.title
        )

    def test_create_borrowing_no_inventory(self):
        self.book.inventory = 0
        self.book.save()
        response = self.client.post(
            "/api/borrowing_service/borrow/", self.borrowing_data
        )
        print(str(response.data[0]))
        self.assertEqual(response.status_code, 400)
        self.assertIn("No books left", str(response.data[0]))

    def test_retrieve_borrowing(self):
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        response = self.client.get(f"/api/borrowing_service/borrow/{borrowing.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Book.objects.get(id=response.data["book"]).title, self.book.title
        )

    def test_update_borrowing_unauthorized(self):
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        response = self.client.put(
            f"/api/borrowing_service/borrow/{borrowing.id}/", self.borrowing_data
        )
        self.assertEqual(response.status_code, 403)

    def test_update_borrowing_authorized(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin_user).access_token}"
        )
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        updated_data = {
            "borrow_date": datetime.today().strftime("%Y-%m-%d"),
            "expected_return": (datetime.today() + timedelta(days=14)).strftime(
                "%Y-%m-%d"
            ),
            "book": self.book.id,
        }
        response = self.client.put(
            f"/api/borrowing_service/borrow/{borrowing.id}/", updated_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(
            response.data["expected_return"], updated_data["expected_return"]
        )

    def test_return_book(self):
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        response = self.client.post(
            "/api/borrowing_service/return/", {"borrowing_id": borrowing.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, "You returned this book")

    def test_return_book_already_returned(self):
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            actual_return=datetime.today(),
            book=self.book,
            user=self.user,
        )
        response = self.client.post(
            "/api/borrowing_service/return/", {"borrowing_id": borrowing.id}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, "You have already returned this book")

    def test_return_book_unauthorized(self):
        borrowing = BorrowingService.objects.create(
            borrow_date=datetime.today(),
            expected_return=datetime.today() + timedelta(days=7),
            book=self.book,
            user=self.admin_user,
        )
        response = self.client.post(
            "/api/borrowing_service/return/", {"borrowing_id": borrowing.id}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, "Borrowing must belong to you")
