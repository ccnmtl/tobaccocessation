from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson

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
        