from django.contrib import admin
from tobaccocessation.activity_prescription_writing.models import Medication, \
    ActivityState


class ActivityStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'block')
    search_fields = ['user__username']


admin.site.register(ActivityState, ActivityStateAdmin)
admin.site.register(Medication)
