from rest_framework import serializers

from book_service.models import Book
from book_service.serializers import BookSerializer
from borrowing_service.models import BorrowingService


class BorrowingServiceReadSerializer(serializers.ModelSerializer):
    book = BookSerializer
    user = serializers.CharField(source="user.email")

    class Meta:
        model = BorrowingService
        fields = "__all__"


def check_inventory(pk: int) -> bool:
    return Book.objects.get(pk=pk).inventory > 0


def reduce_inventory(pk: int) -> None:
    Book.objects.get(pk=pk).inventory -= 1


class BorrowingServiceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BorrowingService
        fields = ["borrow_date", "expected_return", "actual_return", "book"]

    def create(self, **validated_data):
        book_id = validated_data["book"]
        if check_inventory(book_id):
            reduce_inventory(book_id)
            BorrowingService.objects.create(
                **validated_data, user=self.context["request"].user
            )
