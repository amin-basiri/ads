from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Ads(BaseModel):
    user = models.ForeignKey("pauth.PUser", on_delete=models.CASCADE)
    
    title = models.CharField(max_length=100)

    image = models.ImageField(upload_to="ads/")

    description = models.TextField()


class Comment(BaseModel):
    ads = models.ForeignKey('Ads', on_delete=models.CASCADE)

    user = models.ForeignKey('pauth.PUser', on_delete=models.CASCADE)

    text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'ads'], name="user_ads_unique")
        ]
