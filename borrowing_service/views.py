from django.shortcuts import render
from rest_framework import viewsets

from borrowing_service.models import BorrowingService
from borrowing_service.serializers import BorrowingServiceReadSerializer


# Create your views here.
class BorrowingServiceViewSet(viewsets.ModelViewSet):
    queryset = BorrowingService.objects.all().select_related("book_service.Book", "user.User")

    def get_serializer_class(self):
        if self.action in ["list", "detail"]:
            return BorrowingServiceReadSerializer
        else:
            pass
