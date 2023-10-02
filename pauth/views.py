import logging

from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from pauth import models
from pauth import serializers
from ads.views import BaseView

logger = logging.getLogger(__name__)


class UserViewSet(BaseView):
    lookup_field = "id"
    queryset = models.PUser.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=["get"])
    def me(self, request):
        user = self.get_serializer(instance=self.request.user)
        return Response(user.data, status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        authentication_classes=(),
        permission_classes=[permissions.AllowAny],
    )
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            serializers.UserSerializer(instance=user).data,
            status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
    )
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        user = authenticate(
            request=request,
            email=email,
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                data={"detail": "Invalid username/password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def sign_out(self, request):
        request.user.auth_token.delete()
        return Response({"Success": "logout and token removed"}, status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == "sign_up":
            return serializers.SignupSerializer
        elif self.action == "sign_in":
            return serializers.SigninSerializer
        elif self.action == "me":
            return serializers.UserSerializer
        else:
            return self.serializer_class
