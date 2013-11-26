from django.contrib import admin
from pagetree.models import Hierarchy
from tobaccocessation.main.models import UserProfile, UserVisit


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'is_faculty', 'role', 'institute']


class UserVisitAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', 'section', 'count', 'created', 'modified']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserVisit, UserVisitAdmin)
admin.site.register(Hierarchy)
