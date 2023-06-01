from django.contrib import admin

# Register your models here.
from .models import Room, Message, Company, User, Notification, Application, Selected

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Company)
#only do this if you are using custom user model
admin.site.register(User)
admin.site.register(Notification)
admin.site.register(Application)
admin.site.register(Selected)