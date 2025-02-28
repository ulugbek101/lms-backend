from django.contrib import admin
from django.contrib.auth.models import Group

from . import models

admin.site.unregister(Group)
admin.site.register(models.User)
admin.site.register(models.SuperAdmin)
admin.site.register(models.Admin)
admin.site.register(models.Teacher)
admin.site.register(models.Parent)
admin.site.register(models.Student)
admin.site.register(models.Payment)
admin.site.register(models.Group)
admin.site.register(models.Subject)
admin.site.register(models.Room)
