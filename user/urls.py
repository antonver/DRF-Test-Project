from django.urls import path
from user.views import CreateUserView, CreateTokenView, ManageUserView, UserChatId

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("chat_id/", UserChatId.as_view(), name="change"),
]
