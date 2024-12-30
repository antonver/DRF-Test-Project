from django.db import models


class BorrowingService(models.Model):
    borrow_date = models.DateField()
    expected_return = models.DateField()
    actual_return = models.DateField(blank=True, null=True)
    book = models.ForeignKey("book_service.Book", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["book"]),
        ]

    def clean(self):
        if self.expected_return < self.borrow_date:
            return False
        if self.actual_return is not None and self.actual_return < self.borrow_date:
            return False

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.expected_return}"
