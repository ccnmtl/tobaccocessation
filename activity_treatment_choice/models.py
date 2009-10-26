from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from django import forms

class Block(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activity_treatment_choice/treatment.html"
    display_name = "Activity: Treatment Choice"
    treatments = [ 'patch', 'gum', 'inhaler', 'lozenge', 'nasalspray', 'chantix', 'bupropion', 'combination'  ]
    
    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False
    
    def unlocked(self,user):
        return True
    
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

class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="treatment_choice_user")
    json = models.TextField(blank=True)
    
    def __json__(self):
        shim = {}
        shim['name'] = self.name
        
        # levels
        shim['levels'] = []
        for level in self.supportlevel_set.all():
            dict = {}
            dict['id'] = level.id
            dict['name'] = level.name
            dict['color'] = level.color
            dict['icon'] = level.icon
            shim['levels'].append(dict)
        
        # types
        shim['types'] = []
        for type in self.supporttype_set.all():
            dict = {}
            dict['id'] = type.id
            dict['name'] = type.name
            dict['icon'] = type.icon
            shim['types'].append(dict)
        
        return simplejson.dumps(shim)
    
    