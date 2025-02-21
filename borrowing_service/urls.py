from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import BorrowingServiceViewSet, BorrowingServiceReturnView

router = DefaultRouter()
router.register(r"borrow", BorrowingServiceViewSet)

urlpatterns = [
    path("return/", BorrowingServiceReturnView.as_view(), name="return"),
]
urlpatterns += router.urls

app_name = "borrowing_service"
