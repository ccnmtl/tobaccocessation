from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from pagetree.models import Section
from tobaccocessation.activity_virtual_patient.models import ActivityState


@login_required
def reset(request, section_id, patient_id):
    section = Section.objects.get(id=section_id)

    ActivityState.clear_for_user(request.user, section.hierarchy, patient_id)
    return HttpResponseRedirect(section.get_parent().get_absolute_url())
