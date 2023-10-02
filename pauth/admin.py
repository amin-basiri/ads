from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pauth import models


class CustomUserAdmin(UserAdmin):
    list_display = ["email", "first_name", "last_name"]


admin.site.register(models.PUser, CustomUserAdmin)
