from django.db import models
from django.contrib.auth.models import User

class SiteState(models.Model):
    user = models.ForeignKey(User, related_name="application_user")
    last_location = models.CharField(max_length=255)
    
    @staticmethod
    def save_last_location(user, path):
        ss = SiteState.objects.get_or_create(user=user)
        ss[0].last_location = path
        ss[0].save()