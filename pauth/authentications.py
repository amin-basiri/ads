from django.contrib.auth.backends import ModelBackend

from pauth import models


class EmailAuthentication(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = models.PUser.objects.get(email=email)

        except models.PUser.DoesNotExist:
            return None

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = models.PUser.objects.get(pk=user_id)
        except models.PUser.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
