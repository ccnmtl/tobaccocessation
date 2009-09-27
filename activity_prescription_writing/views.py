from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django import forms

@login_required
def root(request):
    
    ctx = Context({
       'user': request.user
    })
    
    template = loader.get_template('activity_prescription_writing/prescription.html')
    return HttpResponse(template.render(ctx))


class PrescriptionForm(forms.Form):
    medication_name = forms.CharField(max_length=100)
    dosage = forms.CharField()
    sig = forms.CharField()
    refills = forms.IntegerField()
