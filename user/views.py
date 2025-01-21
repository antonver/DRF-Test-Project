from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.models import User
from user.serializers import UserSerializer, AuthTokenSerializer, UserChatIdSerializer


class CreateUserView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserChatId(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserChatIdSerializer

    def get_object(self, queryset=None):
        return self.request.user
