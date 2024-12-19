from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrowing_service.models import BorrowingService


class BorrowingServiceReadSerializer(serializers.ModelSerializer):
    book = BookSerializer

    class Meta:
        model = BorrowingService
        fields = '__all__'
