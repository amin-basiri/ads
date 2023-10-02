from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ads import models


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = [
            "user",
            "text",
            "ads"
        ]
        read_only_fields = ['user', ]
        extra_kwargs = {
            'ads': {'write_only': True},
        }

    def validate(self, attrs):
        if models.Comment.objects.filter(
            user=self.context["request"].user,
            ads_id=attrs["ads"]
        ).exists():
            raise ValidationError("You already commented on this ad!")
        return attrs

    def get_user(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def create(self, validated_data):
        validated_data.update({
            "user": self.context["request"].user
        })
        return super().create(validated_data)


class AdSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = models.Ads
        fields = [
            "id",
            "title",
            "image",
            "description",
            "comments",
        ]
        read_only_fields = ['comments', "id"]

    def create(self, validated_data):
        validated_data.update(
            {
                "user": self.context["request"].user
            }
        )
        return super().create(validated_data=validated_data)

    def get_comments(self, obj: models.Ads):
        if obj.comment_set.exists():
            return CommentSerializer(instance=obj.comment_set.all(), many=True).data
        return []
