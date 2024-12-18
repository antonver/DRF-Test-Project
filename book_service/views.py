from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from book_service.models import Book
from book_service.serializers import BookSerializer


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()
