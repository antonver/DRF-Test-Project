from datetime import datetime
from dateutil.relativedelta import relativedelta

import telebot
from celery import shared_task

from book_service.models import Book
from borrowing_service.models import BorrowingService
from drf_task_project import settings
from user.models import User

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@shared_task
def notification():
    users = User.objects.all()
    today = datetime.today().date()
    tomorrow = (datetime.today() + relativedelta(days=1)).date()

    for user in users:
        if user.chat_id is None:
            continue

        messages = ["Hello! Here's some information about your borrowings:\n"]
        has_borrowings = False

        borrowings = BorrowingService.objects.filter(user=user)
        for borrowing in borrowings:
            if borrowing.actual_return is None:
                if borrowing.expected_return == tomorrow:
                    messages.append(
                        f"Your borrowing with id: {borrowing.id}, "
                        f"book: {borrowing.book.title}, will expire tomorrow. Please return it!\n"
                    )
                    has_borrowings = True
                elif borrowing.expected_return == today:
                    messages.append(
                        f"Your borrowing with id: {borrowing.id}, "
                        f"book: {borrowing.book.title}, expires today. Please return it!\n"
                    )
                    has_borrowings = True
                elif borrowing.expected_return < today:
                    messages.append(
                        f"Your borrowing with id: {borrowing.id}, "
                        f"book: {borrowing.book.title}, expired on {borrowing.expected_return}. "
                        f"Please return it as soon as possible!\n"
                    )
                    has_borrowings = True

        if not has_borrowings:
            messages.append("You don't have any overdue borrowings!")

        try:
            bot.send_message(user.chat_id, "".join(messages))
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {e}")
