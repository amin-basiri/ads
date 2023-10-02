from django.contrib import admin
from ads import models


class AdsAdmin(admin.ModelAdmin):
    # list_display = ["id", 'title', 'user']
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Ads, AdsAdmin)
admin.site.register(models.Comment, CommentAdmin)