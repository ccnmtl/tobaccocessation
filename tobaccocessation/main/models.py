from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from pagetree.models import PageBlock, Section
from registration.forms import RegistrationForm


class Role(models.Model):
    STUDENT = 'ST'
    PERIO = 'PR'
    ORAL_SURGERY = 'OS'
    GEN_PRACTICE = 'GP'

    ROLE_CHOICES = (

        (STUDENT, 'Student'),
        (PERIO, 'Perio'),
        (ORAL_SURGERY, 'Oral Surgeon'),
        (GEN_PRACTICE, 'General Practitioner'),
    )
    name = models.CharField(max_length=2, choices=ROLE_CHOICES)

    def __unicode__(self):
        return self.name


class UserVisit(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
    count = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "section")


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="application_user")
    role = models.ForeignKey(Role, null=True, blank=True)
    visits = models.ManyToManyField(UserVisit, null=True, blank=True)

    def __unicode__(self):
        return self.user.username

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

    def get_has_visited(self, section):
        return len(self.visits.filter(user=self.user, section=section)) > 0

    def set_has_visited(self, sections):
        for sect in sections:
            visits = self.visits.filter(user=self.user,
                                        section=sect)
            if len(visits) > 0:
                visits[0].count = visits[0].count + 1
                visits[0].save()
            else:
                visit = UserVisit(user=self.user, section=sect)
                visit.save()
                self.visits.add(visit)

    def get_last_location(self):
        visits = self.visits.filter(user=self.user).order_by('-modified')
        if len(visits) > 0:
            return visits[0].section
        else:
            return None

    def display_name(self):
        return self.user.username


class UserProfileForm(forms.Form):
    '''Form which will be used to obtain further
    information from the user.'''
#     #first_name = forms.CharField(max_length=256)
#     #last_name = forms.CharField(max_length=256)
#     #gender = forms.ChoiceField(
#     #    initial="-----", choices=GENDER_CHOICES, label='Your gender')

    role = forms.ChoiceField(
        choices=Role.ROLE_CHOICES,
        label="Select your role in this course")
#     #dental_school = models.CharField(max_length=1024,
#     #                                choices=DENTAL_SCHOOL_CHOICES)


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
