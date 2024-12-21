from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowing_service.models import BorrowingService
from borrowing_service.serializers import (
    BorrowingServiceReadSerializer,
    BorrowingServiceCreateSerializer,
)


# Create your views here.
class BorrowingServiceViewSet(viewsets.ModelViewSet):
    queryset = BorrowingService.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "detail"]:
            return BorrowingServiceReadSerializer
        else:
            return BorrowingServiceCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        print(self.request.user.id)
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
        if self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated()]
        return super().get_permissions()
