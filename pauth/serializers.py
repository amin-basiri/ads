from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from pauth import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PUser
        fields = [
            "email",
            "first_name",
            "last_name",
        ]


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address",
        },
        validators=[
            UniqueValidator(
                queryset=models.PUser.objects.all(),
                message="This email already used",
            ),
        ],
    )

    first_name = serializers.CharField()

    last_name = serializers.CharField()

    password = serializers.CharField(min_length=8, max_length=30)

    def create(self, validated_data):
        user = models.PUser.objects.create_user(
            **validated_data
        )

        return user


class SigninSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField()
