from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from django import forms
from django.utils import simplejson

class Block(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activity_treatment_choice/treatment.html"
    display_name = "Activity: Treatment Choice"
    treatments = [ 'patch', 'bupropion', 'nasalspray', 'lozenge', 'inhaler', 'chantix',  'gum', 'combination'  ]
    
    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False
    
    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            dummy=True
        return AddForm()

    @classmethod
    def create(self,request):
        return Block.objects.create()
    
    @classmethod
    def edit_form(self):
        class EditForm(forms.Form):
            dummy=True
        return EditForm();
    
    @classmethod
    def edit(self,vals,files):
        self.save()
        
    def unlocked(self, user):
        rc = False
        try:
            state = ActivityState.objects.get(user=user)
            obj = simplejson.loads(state.json)
            if obj.has_key('complete'):
                rc = obj['complete']
        except ActivityState.DoesNotExist:
            pass # ignore, we'll return false here in a sec
        
        return rc
        
class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="treatment_choice_user")
    json = models.TextField(blank=True)
