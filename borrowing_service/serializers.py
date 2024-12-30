from rest_framework import serializers

from book_service.models import Book
from book_service.serializers import BookReadSerializer
from borrowing_service.models import BorrowingService


class BorrowingServiceReadSerializer(serializers.ModelSerializer):
    book = BookReadSerializer
    user_email = serializers.CharField(source="user.email")
    user_id = serializers.IntegerField(source="user.id")

    class Meta:
        model = BorrowingService
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book",
            "user_email",
            "user_id",
        ]


def check_inventory(pk: int) -> bool:
    return Book.objects.get(pk=pk).inventory > 0


def reduce_inventory(pk: int) -> None:
    book = Book.objects.get(pk=pk)
    book.inventory -= 1
    book.save()


class BorrowingServiceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BorrowingService
        fields = ["borrow_date", "expected_return", "actual_return", "book"]

    def create(self, validated_data):
        user = validated_data.pop("user")
        book = validated_data["book"]
        if check_inventory(book.id):
            reduce_inventory(book.id)
            borrow = BorrowingService.objects.create(user=user, **validated_data)
            return borrow
        else:
            raise serializers.ValidationError("No books left")


class BorrowingServiceChangeSerializer(serializers.Serializer):
    borrowing_id = serializers.IntegerField()
