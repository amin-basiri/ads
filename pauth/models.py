from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from ads.models import BaseModel


class PUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email,name, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user
    

class PUser(AbstractUser, BaseModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True)

    objects = PUserManager()

    def __str__(self) -> str:
        return self.email
