from tobaccocessation.activity_virtual_patient.models import *
from django.contrib import admin

class MedicationDosageChoiceInline(admin.TabularInline):
    model = DosageChoice
    max_num = 4
    extra = 4
    
class MedicationRefillChoiceInline(admin.TabularInline):
    model = RefillChoice
    max_num = 4
    extra = 4

class MedicationConcentrationChoiceInline(admin.TabularInline):
    model = ConcentrationChoice
    max_num = 4
    extra = 4

class MedicationAdmin(admin.ModelAdmin):
    inlines = [
        MedicationConcentrationChoiceInline,
        MedicationDosageChoiceInline,
        MedicationRefillChoiceInline
    ]
admin.site.register(Medication, MedicationAdmin)

admin.site.register(TreatmentClassification)

class TreatmentOptionReasoningInline(admin.TabularInline):
    model = TreatmentOptionReasoning
    extra = 3
    
class TreatmentOptionInline(admin.TabularInline):
    model = TreatmentOption
    extra = 6
    
class TreatmentFeedbackInline(admin.TabularInline):
    model = TreatmentFeedback
    max_num = 5
    extra = 5
    
class PatientAdmin(admin.ModelAdmin):
    inlines = [ 
        TreatmentOptionInline,
        TreatmentFeedbackInline,
        TreatmentOptionReasoningInline,
    ]
    
admin.site.register(Patient, PatientAdmin)

