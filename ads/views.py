from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   DestroyModelMixin, UpdateModelMixin)

from ads import models
from ads import serializers
from ads import permissions as ads_permissions
from ads.exceptions import ads_api_exception_handler


class BaseView(GenericViewSet):
    def get_exception_handler(self):
        return ads_api_exception_handler


class AdViewSet(
    BaseView,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    UpdateModelMixin
):
    queryset = models.Ads.objects.all()
    serializer_class = serializers.AdSerializer

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        self.get_object()
        serializer = self.get_serializer(
            data={
                "ads": pk,
                **self.request.data,
            }
        )
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()

        return Response(
            serializers.CommentSerializer(instance=comment).data,
            status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)

        return Response({"msg": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny, ]
        elif self.action in ['destroy', "update", "partial_update"]:
            permission_classes = [permissions.IsAuthenticated, ads_permissions.IsOwnedByUser, ]
        else:
            permission_classes = [permissions.IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "comment":
            return serializers.CommentSerializer
        return self.serializer_class
