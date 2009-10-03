from tobaccocessation.activity_virtual_patient.models import *
from django.contrib import admin

class MedicationDosageChoiceInline(admin.TabularInline):
    model = MedicationDosageChoice
    max_num = 4
    extra = 4
    
class MedicationRefillChoiceInline(admin.TabularInline):
    model = MedicationRefillChoice
    max_num = 4
    extra = 4

class MedicationConcentrationChoiceInline(admin.TabularInline):
    model = MedicationConcentrationChoice
    max_num = 4
    extra = 4

class MedicationAdmin(admin.ModelAdmin):
    inlines = [
        MedicationConcentrationChoiceInline,
        MedicationDosageChoiceInline,
        MedicationRefillChoiceInline
    ]
admin.site.register(Medication, MedicationAdmin)

