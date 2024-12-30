from datetime import datetime

from django.shortcuts import render, get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
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
        if self.action in ["list", "retrieve"]:
            return BorrowingServiceReadSerializer
        else:
            return BorrowingServiceCreateSerializer

    @extend_schema(
        responses=BorrowingServiceCreateSerializer,
        description="Create a new borrowing service entry. Sends a notification to the user's chat if chat_id is available.",
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        if self.request.user.chat_id is not None:
            bot.send_message(
                self.request.user.chat_id,
                f"You have just borrowed a new book: {Book.objects.get(id=serializer.data['book']).title}",
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings, it has no value, just parameter",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID (admin only)",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        responses=BorrowingServiceReadSerializer(many=True),
        description="Retrieve a list of borrowing services. Admins can filter by user ID.",
    )
    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user.id)
        if self.action in ["list", "retrieve"]:
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


@extend_schema(
    methods=["POST"],
    request=BorrowingServiceChangeSerializer,
    responses={
        200: OpenApiResponse(description="You returned this book"),
        400: OpenApiResponse(
            description="Borrowing must belong to you or You have already returned this book"
        ),
        401: OpenApiResponse(description="Not authorized"),
    },
    description="Endpoint to return a borrowed book. Requires authentication.",
)
@extend_schema(
    methods=["GET"],
    responses={
        200: BorrowingServiceReadSerializer(many=True),
        401: OpenApiResponse(description="Not authorized"),
    },
    description="Endpoint to retrieve the list of borrowed books that have not been returned. Requires authentication.",
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def return_date(request):
    if request.method == "POST":
        serializer = BorrowingServiceChangeSerializer(data=request.data)
        if serializer.is_valid():
            borrowing_id = serializer.validated_data.get("borrowing_id")
            borrowing = get_object_or_404(BorrowingService, pk=borrowing_id)
            if borrowing.user != request.user:
                return Response(
                    "Borrowing must belong to you", status=status.HTTP_400_BAD_REQUEST
                )
            if borrowing.actual_return is not None:
                return Response(
                    "You have already returned this book",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                borrowing.actual_return = datetime.today()
                borrowing.save()
                book = Book.objects.get(id=borrowing.book.id)
                book.inventory += 1
                book.save()
                return Response("You returned this book", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "GET":
        serializer = BorrowingServiceReadSerializer(
            BorrowingService.objects.filter(user=request.user, actual_return=None),
            many=True,
        )
        return Response(
            {"message": "Your borrowings", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
