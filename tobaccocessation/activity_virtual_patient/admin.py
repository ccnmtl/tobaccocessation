from django.contrib import admin
from tobaccocessation.activity_virtual_patient.models import DosageChoice, \
    RefillChoice, ConcentrationChoice, Medication, Patient, \
    TreatmentClassification, TreatmentOptionReasoning, TreatmentOption, \
    TreatmentFeedback, ActivityState


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
    list_display = ('tag', 'name', 'display_order')

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
    max_num = 6
    extra = 5


class PatientAdmin(admin.ModelAdmin):
    save_as = True
    inlines = [
        TreatmentOptionInline,
        TreatmentFeedbackInline,
        TreatmentOptionReasoningInline,
    ]


admin.site.register(Patient, PatientAdmin)
admin.site.register(ActivityState)
