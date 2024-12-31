from rest_framework import serializers

from book_service import models


class BookReadSerializer(serializers.ModelSerializer):
    cover = serializers.CharField(source="get_cover_display", read_only=True)

    class Meta:
        model = models.Book
        fields = "__all__"


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = "__all__"
