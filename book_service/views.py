from django.shortcuts import render
from rest_framework import viewsets

from book_service.models import Book
from book_service.serializers import BookSerializer


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

