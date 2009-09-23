from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def root(request):
    return render_to_response("activity_treatment_choice/index.html", dict(user=request.user))

@login_required
def treatment(request):
    treatments = [ 'patch', 'gum', 'inhaler', 'lozenge', 'nasalspray', 'chantix', 'bupropion', 'combination'  ]
    
    ctx = Context({
       'user': request.user,
       'treatments': treatments,
    })
    
    template = loader.get_template('activity_treatment_choice/treatment.html')
    return HttpResponse(template.render(ctx))
