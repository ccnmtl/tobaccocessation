from django.contrib import admin
from pagetree.models import Hierarchy
from tobaccocessation.main.models import UserProfile, UserVisit


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ["visits"]
    search_fields = ['user__username']
    list_display = ['user', 'is_faculty', 'role', 'institute']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Hierarchy)
