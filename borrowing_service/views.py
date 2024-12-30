from datetime import datetime

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
import telebot
from book_service.models import Book
from borrowing_service.models import BorrowingService
from borrowing_service.serializers import (
    BorrowingServiceReadSerializer,
    BorrowingServiceCreateSerializer,
    BorrowingServiceChangeSerializer,
)
from drf_task_project import settings

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


# Create your views here.
class BorrowingServiceViewSet(viewsets.ModelViewSet):
    chat_id = None
    queryset = BorrowingService.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "detail"]:
            return BorrowingServiceReadSerializer
        else:
            return BorrowingServiceCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        if self.request.user.chat_id is not None:
            bot.send_message(
                self.request.user.chat_id,
                f"You have just borrowed a new book: {Book.objects.get(id=serializer.data['book']).title}",
            )

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user.id)
        if self.action in ["list", "detail"]:
            queryset = queryset.select_related("book", "user")
        else:
            queryset = queryset.select_related("book")
        if "is_active" in self.request.query_params:
            queryset = queryset.filter(actual_return__isnull=True)
        if (
            self.request.query_params.get("user_id") is not None
            and self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                user__id=self.request.query_params.get("user_id")
            )
        return queryset

    def get_permissions(self):
        if self.action in ["create", "list"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:
            return [IsAdminUser()]
        return super().get_permissions()


@api_view(["GET", "POST"])
def return_date(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            serializer = BorrowingServiceChangeSerializer(data=request.data)
            if serializer.is_valid():
                borrowing_id = serializer.data.get("borrowing_id")
                borrowing = get_object_or_404(BorrowingService, pk=borrowing_id)
                if borrowing.user != request.user:
                    return Response("Borrowing must belong to you", status=400)
                if borrowing.actual_return is not None:
                    return Response("You have already returned this book", status=400)
                else:
                    borrowing.actual_return = datetime.today()
                    borrowing.save()
                    book = Book.objects.get(id=borrowing.book.id)
                    book.inventory += 1
                    book.save()
                    return Response("You returned this book", status=200)
        else:
            return Response("Not authorized", status=401)
    elif request.method == "GET":
        if request.user.is_authenticated:
            serializer = BorrowingServiceReadSerializer(
                BorrowingService.objects.filter(user=request.user, actual_return=None),
                many=True,
            )
            return Response(
                {"message": "Your borrowings", "data": serializer.data}, status=200
            )
