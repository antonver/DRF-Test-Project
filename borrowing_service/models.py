from django.db import models


class BorrowingService(models.Model):
    borrow_date = models.DateField()
    expected_return = models.DateField()
    actual_return = models.DateField(blank=True, null=True)
    book = models.ForeignKey("book_service.Book", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    def clean(self):
        if (
            self.expected_return < self.borrow_date
            or self.actual_return < self.borrow_date
        ):
            return False

    def save(self, *args, **kwargs):
        self.full_clean(*args, **kwargs)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.expected_return
