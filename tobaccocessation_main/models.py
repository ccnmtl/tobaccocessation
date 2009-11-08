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
    
    def __init__(self, *args, **kwargs):
        super(SiteState, self).__init__(*args, **kwargs)
        
        self._refresh_state_object()
    
    def get_has_visited(self, section):
        return self.state_object.has_key(str(section.id))
    
    def set_has_visited(self, sections):
        for s in sections:
            self.state_object[s.id] = s.label
            
        self.visited = simplejson.dumps(self.state_object)
        self.save()
        self._refresh_state_object()
    
    def save_last_location(self, path, section):
        self.state_object[section.id] = section.label
        self.last_location = path
        self.visited = simplejson.dumps(self.state_object)
        self.save()
        self._refresh_state_object()
        
    def _refresh_state_object(self):
        if (len(self.visited) > 0): 
            self.state_object = simplejson.loads(self.visited)
        else:
            self.state_object = {}
        
        
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