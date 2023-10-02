from django.contrib import admin
from pauth import models


class UserAdmin(admin.ModelAdmin):
    pass


# admin.site.register(models.Ads, AdsAdmin)