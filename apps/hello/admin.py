from django.contrib import admin
from .models import AboutMe, RequestContent, ModelsChange
from .models import Thread, Message


class AdminModelsChanges(admin.ModelAdmin):
    list_display = ('model', 'datetime', 'action')


class AdminThread(admin.ModelAdmin):
    list_display = ('get_participants',)


admin.site.register(AboutMe)
admin.site.register(RequestContent)
admin.site.register(ModelsChange, AdminModelsChanges)
admin.site.register(Thread, AdminThread)
admin.site.register(Message)
