from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from ads.models import BaseModel


class PUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user
    

class PUser(AbstractUser, BaseModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    objects = PUserManager()

    def __str__(self) -> str:
        return self.email
