from django.contrib import admin
from .models import Yacht, Request, UserInfo

admin.site.register(Yacht)
admin.site.register(Request)
admin.site.register(UserInfo)