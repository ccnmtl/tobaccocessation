from django import forms
from django.contrib.auth.models import User
from django.db import models
from pagetree.models import Hierarchy, UserLocation, UserPageVisit
from registration.forms import RegistrationForm
from registration.signals import user_registered
from tobaccocessation.main.choices import GENDER_CHOICES, FACULTY_CHOICES, \
    INSTITUTION_CHOICES, SPECIALTY_CHOICES, RACE_CHOICES, AGE_CHOICES, \
    HISPANIC_LATINO


class UserProfile(models.Model):
    #  ALL_CU group affiliations
    user = models.ForeignKey(User, related_name="application_user",
                             unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_faculty = models.CharField(max_length=2,
                                  choices=FACULTY_CHOICES)
    institute = models.CharField(max_length=2,
                                 choices=INSTITUTION_CHOICES)
    specialty = models.CharField(max_length=3,
                                 choices=SPECIALTY_CHOICES)
    hispanic_latino = models.CharField(max_length=1,
                                       choices=HISPANIC_LATINO)
    # I was not sure whether or not to make year_of_graduation required
    # if someone self registers or is a student they may not have graduated
    year_of_graduation = models.PositiveIntegerField(blank=True)
    consent = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def display_name(self):
        return self.user.username

    def has_consented(self):
        return self.consent

    def is_role_student(self):
        return self.is_faculty == 'ST'

    def is_role_faculty(self):
        return self.is_faculty == 'FA'

    def role(self):
        if (self.is_role_student() or
            self.specialty in ['S2', 'S9', 'S10'] or
                self.specialty is None):
            # Pre-Doctoral Student, Other, Dental Public Health
            return "main"
        elif self.specialty in ['S1', 'S7']:
            # General Practice, Prosthodontics
            return "general"
        elif self.specialty == 'S4':
            # Oral and Maxillofacial Surgery
            return "surgery"
        elif self.specialty == 'S6':
            # Periodontics
            return 'perio'
        elif self.specialty == 'S5':
            # Pediatrics
            return "pediatrics"
        elif self.specialty == 'S8':
            return "orthodontics"
        elif self.specialty == 'S3':
            return "endodontics"

    def get_has_visited(self, section):
        return section.get_uservisit(self.user) is not None

    def set_has_visited(self, sections):
        for sect in sections:
            sect.user_pagevisit(self.user, "complete")
            sect.user_visit(self.user)

    def last_location(self):
        hierarchy = Hierarchy.get_hierarchy(self.role())
        try:
            UserLocation.objects.get(user=self.user,
                                     hierarchy=hierarchy)
            return hierarchy.get_user_section(self.user)
        except UserLocation.DoesNotExist:
            return hierarchy.get_first_leaf(hierarchy.get_root())

    def percent_complete(self):
        hierarchy = Hierarchy.get_hierarchy(self.role())
        pages = len(hierarchy.get_root().get_descendants()) + 1
        visits = UserPageVisit.objects.filter(user=self.user,
                                              section__hierarchy=hierarchy)
        if pages:
            return int(len(visits) / float(pages) * 100)
        else:
            return 0


class QuickFixProfileForm(forms.Form):
    consent = forms.BooleanField(required=True)
    is_faculty = forms.ChoiceField(choices=FACULTY_CHOICES, required=True)
    institute = forms.ChoiceField(choices=INSTITUTION_CHOICES, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    year_of_graduation = forms.IntegerField(
        min_value=1900, max_value=3000,
        label="What year did you graduate?", required=True)
    race = forms.ChoiceField(choices=RACE_CHOICES, required=True)
    hispanic_latino = forms.ChoiceField(choices=HISPANIC_LATINO, required=True)
    age = forms.ChoiceField(choices=AGE_CHOICES, required=True)
    specialty = forms.ChoiceField(choices=SPECIALTY_CHOICES, required=True)

    def clean_is_faculty(self):
        data = self.cleaned_data['is_faculty']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate whether you are faculty or a student.")

    def clean_institute(self):
        data = self.cleaned_data['institute']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate what institution you are affiliated with.")

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if data == '-----':
            raise forms.ValidationError("Please indicate your gender.")

    def clean_year_of_graduation(self):
        data = self.cleaned_data['year_of_graduation']
        if data == '-----':
            raise forms.ValidationError(
                "Please enter your year of graduation.")

    def clean_race(self):
        data = self.cleaned_data['race']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate your race.")

    def clean_hispanic_latino(self):
        data = self.cleaned_data['hispanic_latino']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate if you are hispanic or latino.")

    def clean_age(self):
        data = self.cleaned_data['age']
        if data == '-----':
            raise forms.ValidationError("Please select an age.")

    def clean_specialty(self):
        data = self.cleaned_data['specialty']
        if data == '-----':
            raise forms.ValidationError("Please select a specialty.")


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
    consent = forms.BooleanField(required=True)
    is_faculty = forms.ChoiceField(required=True, choices=FACULTY_CHOICES)
    institute = forms.ChoiceField(choices=INSTITUTION_CHOICES, required=True)
    gender = forms.ChoiceField(required=True, initial="-----",
                               choices=GENDER_CHOICES)
    year_of_graduation = forms.IntegerField(
        required=True, min_value=1900, max_value=3000,
        label="What year did you graduate?")
    race = forms.ChoiceField(required=True, choices=RACE_CHOICES)
    hispanic_latino = forms.ChoiceField(required=True, choices=HISPANIC_LATINO)
    age = forms.ChoiceField(required=True, choices=AGE_CHOICES)
    specialty = forms.ChoiceField(required=True, choices=SPECIALTY_CHOICES)

    def clean_is_faculty(self):
        data = self.cleaned_data['is_faculty']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate whether you are faculty or a student.")

    def clean_institute(self):
        data = self.cleaned_data['institute']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate what institution you are affiliated with.")

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if data == '-----':
            raise forms.ValidationError("Please indicate your gender.")

    def clean_year_of_graduation(self):
        data = self.cleaned_data['year_of_graduation']
        if data == '-----':
            raise forms.ValidationError(
                "Please enter your year of graduation.")

    def clean_race(self):
        data = self.cleaned_data['race']
        if data == '-----':
            raise forms.ValidationError("Please indicate your race.")

    def clean_hispanic_latino(self):
        data = self.cleaned_data['hispanic_latino']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate if you are hispanic or latino.")

    def clean_age(self):
        data = self.cleaned_data['age']
        if data == '-----':
            raise forms.ValidationError("Please select an age.")

    def clean_specialty(self):
        data = self.cleaned_data['specialty']
        if data == '-----':
            raise forms.ValidationError("Please select a specialty.")


def user_created(sender, user, request, **kwargs):
    form = CreateAccountForm(request.POST)

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)

    profile.institute = form.data['institute']
    profile.consent = True
    profile.is_faculty = form.data['is_faculty']
    profile.year_of_graduation = form.data['year_of_graduation']
    profile.specialty = form.data['specialty']
    profile.gender = form.data['gender']
    profile.hispanic_latino = form.data['hispanic_latino']
    profile.race = form.data['race']
    profile.age = form.data['age']
    profile.save()


user_registered.connect(user_created)
