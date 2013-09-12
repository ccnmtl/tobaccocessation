from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from tobaccocessation.activity_treatment_choice.models import ActivityState


@login_required
def loadstate(request):
    try:
        state = ActivityState.objects.get(user=request.user)
        if (len(state.json) > 0):
            doc = state.json
    except ActivityState.DoesNotExist:
        doc = "{}"

    response = HttpResponse(doc, 'application/json')
    response['Cache-Control'] = 'max-age=0,no-cache,no-store'
    return response


@login_required
def savestate(request):
    json = request.POST['json']

    try:
        state = ActivityState.objects.get(user=request.user)
        state.json = json
        state.save()
    except ActivityState.DoesNotExist:
        state = ActivityState.objects.create(user=request.user, json=json)

    response = {}
    response['success'] = 1

    return HttpResponse(simplejson.dumps(response), 'application/json')
