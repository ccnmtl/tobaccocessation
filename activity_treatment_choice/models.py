from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson

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
    
    