from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from django import forms

class SiteState(models.Model):
    user = models.ForeignKey(User, related_name="application_user")
    last_location = models.CharField(max_length=255)
    visited = models.TextField()
    
    @staticmethod
    def save_last_location(user, path, section):
        ss = SiteState.objects.get_or_create(user=user)
        
        if (len(ss[0].visited) > 0): 
            obj = simplejson.loads(ss[0].visited)
        else:
            obj = {}
            
        obj[section.id] = section.label
        
        ss[0].last_location = path
        ss[0].visited = simplejson.dumps(obj)
        ss[0].save()
        
    @staticmethod
    def get_has_visited(user, section):
        ss = SiteState.objects.get_or_create(user=user)
        
        if len(ss[0].visited) < 1:
            return False
        
        obj = simplejson.loads(ss[0].visited)
        return obj.has_key(str(section.id))
    
    @staticmethod
    def set_has_visited(user, sections):
        ss = SiteState.objects.get_or_create(user=user)
        
        if (len(ss[0].visited) > 0): 
            obj = simplejson.loads(ss[0].visited)
        else:
            obj = {}
        
        for s in sections:
            obj[s.id] = s.label
            
        ss[0].visited = simplejson.dumps(obj)
        ss[0].save()
        
        
class FlashVideoBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    file_url = models.CharField(max_length=512)
    image_url = models.CharField(max_length=512)
    width = models.IntegerField()
    height = models.IntegerField()
    
    template_file = "tobaccocessation_main/flashvideoblock.html"
    display_name = "Flash Video (using JW Player)"


    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def edit_form(self):
        class EditForm(forms.Form):
            file_url = forms.CharField(initial=self.file_url)
            image_url = forms.CharField(initial=self.image_url)
            width = forms.IntegerField(initial=self.width)
            height = forms.IntegerField(initial=self.height)
        return EditForm()

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            file_url = forms.CharField()
            image_url = forms.CharField()
            width = forms.IntegerField()
            height = forms.IntegerField()
        return AddForm()

    @classmethod
    def create(self,request):
        return FlashVideoBlock.objects.create(file_url=request.POST.get('file_url',''), 
                                              image_url=request.POST.get('image_url',''),
                                              width=request.POST.get('width', ''),
                                              height=request.POST.get('height', ''))

    def edit(self,vals,files):
        self.file_url = vals.get('file_url','')
        self.image_url = vals.get('image_url','')
        self.width = vals.get('width','')
        self.height = vals.get('height','')
        self.save()