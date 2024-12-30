from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import BorrowingServiceViewSet, return_date

router = DefaultRouter()
router.register(r"borrow", BorrowingServiceViewSet)

urlpatterns = [
    path("return/", return_date, name="return-date"),
]
urlpatterns += router.urls

app_name = "borrowing_service"
