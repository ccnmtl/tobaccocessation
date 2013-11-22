from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.utils import simplejson
from pagetree.models import PageBlock
from registration.forms import RegistrationForm
from django.dispatch import Signal
from tobaccocessation.main.choices import GENDER_CHOICES, \
    FACULTY_CHOICES, INSTITUTION_CHOICES, SPECIALTY_CHOICES, \
    RACE_CHOICES, AGE_CHOICES, HISPANIC_LATINO

class UserProfile(models.Model):

    user = models.ForeignKey(User, related_name="application_user")
    last_location = models.CharField(max_length=255)
    visited = models.TextField()
    gender = models.CharField(max_length=1, null=True, choices=GENDER_CHOICES)
    is_faculty = models.CharField(max_length=2, null=True, choices=FACULTY_CHOICES)
    institute = models.CharField(max_length=2, null=True, choices=INSTITUTION_CHOICES)
    specialty = models.CharField(max_length=2, null=True, choices=SPECIALTY_CHOICES)
    hispanic_latino = models.CharField(max_length=1, null=True, choices=HISPANIC_LATINO)
    year_of_graduation = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return self.user.username

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

        if (len(self.visited) > 0):
            self.state_object = simplejson.loads(self.visited)
        else:
            self.state_object = {}

    def get_has_visited(self, section):
        has_visited = str(section.id) in self.state_object
        return has_visited

    def set_has_visited(self, sections):
        for s in sections:
            self.state_object[str(s.id)] = s.label

        self.visited = simplejson.dumps(self.state_object)
        self.save()

    def save_last_location(self, path, section):
        self.state_object[str(section.id)] = section.label
        self.last_location = path
        self.visited = simplejson.dumps(self.state_object)
        self.save()

    def display_name(self):
        return self.user.username


class QuickFixProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    is_faculty = forms.ChoiceField(choices=FACULTY_CHOICES)
    institute = forms.ChoiceField(choices=INSTITUTION_CHOICES)
    gender = forms.ChoiceField(initial="-----", choices=GENDER_CHOICES)
    year_of_graduation = forms.IntegerField(
        min_value=1900, max_value=3000,
        label="What year did you graduate?")
    race = forms.ChoiceField(choices=RACE_CHOICES)
    hispanic_latino = forms.ChoiceField(choices=HISPANIC_LATINO)
    age = forms.ChoiceField(choices=AGE_CHOICES)
    specialty = forms.ChoiceField(choices=SPECIALTY_CHOICES)


class ColumbiaUserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'is_faculty', 'specialty', 'year_of_graduation']


class NonColumbiaUserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'is_faculty', 'institute', 'specialty', 'year_of_graduation']



class CreateAccountForm(RegistrationForm):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
    first_name = forms.CharField(
        max_length=25, required=True, label="First Name")
    last_name = forms.CharField(
        max_length=25, required=True, label="Last Name")
    username = forms.CharField(
        max_length=25, required=True, label="Username")
    password1 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Password")
    password2 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Confirm Password")
    email = forms.EmailField()

class FlashVideoBlock(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    file_url = models.CharField(max_length=512)
    image_url = models.CharField(max_length=512)
    width = models.IntegerField()
    height = models.IntegerField()

    template_file = "main/flashvideoblock.html"
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
    def create(self, request):
        return FlashVideoBlock.objects.create(
            file_url=request.POST.get('file_url', ''),
            image_url=request.POST.get(
                'image_url', ''),
            width=request.POST.get(
                'width', ''),
            height=request.POST.get('height', ''))

    def edit(self, vals, files):
        self.file_url = vals.get('file_url', '')
        self.image_url = vals.get('image_url', '')
        self.width = vals.get('width', '')
        self.height = vals.get('height', '')
        self.save()
