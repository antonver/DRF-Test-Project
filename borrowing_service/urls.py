from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import BorrowingServiceViewSet

router = DefaultRouter()
router.register(r"borrow", BorrowingServiceViewSet)

urlpatterns = []
urlpatterns += router.urls
