from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pagetree.models import Hierarchy, UserPageVisit
from quizblock.models import Submission, Response
from registration.forms import RegistrationForm
from registration.signals import user_registered
from tobaccocessation.main.choices import GENDER_CHOICES, FACULTY_CHOICES, \
    INSTITUTION_CHOICES, SPECIALTY_CHOICES, RACE_CHOICES, AGE_CHOICES, \
    HISPANIC_LATINO_CHOICES


class UserProfile(models.Model):
    #  ALL_CU group affiliations
    user = models.OneToOneField(User, related_name="profile", unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_faculty = models.CharField(max_length=2, choices=FACULTY_CHOICES)
    institute = models.CharField(max_length=2, choices=INSTITUTION_CHOICES)
    specialty = models.CharField(max_length=3, choices=SPECIALTY_CHOICES)
    hispanic_latino = models.CharField(max_length=1,
                                       choices=HISPANIC_LATINO_CHOICES)
    race = models.CharField(max_length=2, choices=RACE_CHOICES)

    year_of_graduation = models.PositiveIntegerField(blank=True)
    consent_participant = models.BooleanField(default=False)
    consent_not_participant = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def display_name(self):
        return self.user.username

    def has_consented(self):
        '''We need to make sure it checks both.'''
        if self.consent_participant is True:
            return True
        elif self.consent_not_participant is True:
            return True
        else:
            return False

    def has_content(self):
        return self.role() in ['main', 'general', 'surgery', 'perio']

    def is_role_student(self):
        return self.is_faculty == 'ST'

    def is_role_faculty(self):
        return self.is_faculty == 'FA'

    def role(self):
        if (self.specialty in ['S2', 'S9', 'S10'] or
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
        visits = UserPageVisit.objects.filter(
            user=self.user).order_by('-last_visit')

        if visits.count() < 1:
            return hierarchy.get_first_leaf(hierarchy.get_root())
        else:
            return visits.first().section

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
    is_faculty = forms.ChoiceField(choices=FACULTY_CHOICES, required=True)
    institute = forms.ChoiceField(choices=INSTITUTION_CHOICES, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    year_of_graduation = forms.IntegerField(
        min_value=1900, max_value=3000,
        label="What year did you graduate?", required=True)
    race = forms.ChoiceField(choices=RACE_CHOICES, required=True)
    hispanic_latino = forms.ChoiceField(choices=HISPANIC_LATINO_CHOICES,
                                        required=True)
    age = forms.ChoiceField(choices=AGE_CHOICES, required=True)
    specialty = forms.ChoiceField(choices=SPECIALTY_CHOICES, required=True)
    consent_participant = forms.BooleanField(required=False)
    consent_not_participant = forms.BooleanField(required=False)

    def clean_is_faculty(self):
        data = self.cleaned_data['is_faculty']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate whether you are faculty or a student.")
        return data

    def clean_institute(self):
        data = self.cleaned_data['institute']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate what institution you are affiliated with.")
        return data

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if data == '-----':
            raise forms.ValidationError("Please indicate your gender.")
        return data

    def clean_year_of_graduation(self):
        data = self.cleaned_data['year_of_graduation']
        if data == '-----':
            raise forms.ValidationError(
                "Please enter your year of graduation.")
        return data

    def clean_race(self):
        data = self.cleaned_data['race']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate your race.")
        return data

    def clean_hispanic_latino(self):
        data = self.cleaned_data['hispanic_latino']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate if you are hispanic or latino.")
        return data

    def clean_age(self):
        data = self.cleaned_data['age']
        if data == '-----':
            raise forms.ValidationError("Please select an age.")
        return data

    def clean_specialty(self):
        data = self.cleaned_data['specialty']
        if data == '-----':
            raise forms.ValidationError("Please select a specialty.")
        return data

    def clean(self):
        cleaned_data = super(QuickFixProfileForm, self).clean()
        participant = cleaned_data.get("consent_participant")
        not_participant = cleaned_data.get("consent_not_participant")
        if participant and not_participant:
            # User should only select one field
            raise forms.ValidationError("You can be a participant or not,"
                                        " please select one or the other.")
        if not participant and not not_participant:
            # User should select at least one field
            raise forms.ValidationError("You must consent that you have "
                                        "read the document, whether you "
                                        "participate or not.")
        return cleaned_data


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
    # consent = forms.(required=True)
    consent_participant = forms.BooleanField(required=False)
    consent_not_participant = forms.BooleanField(required=False)
    is_faculty = forms.ChoiceField(required=True, choices=FACULTY_CHOICES)
    institute = forms.ChoiceField(choices=INSTITUTION_CHOICES, required=True)
    gender = forms.ChoiceField(required=True, initial="-----",
                               choices=GENDER_CHOICES)
    year_of_graduation = forms.IntegerField(
        required=True, min_value=1900, max_value=3000,
        label="What year did you graduate?")
    race = forms.ChoiceField(required=True, choices=RACE_CHOICES)
    hispanic_latino = forms.ChoiceField(required=True,
                                        choices=HISPANIC_LATINO_CHOICES)
    age = forms.ChoiceField(required=True, choices=AGE_CHOICES)
    specialty = forms.ChoiceField(required=True, choices=SPECIALTY_CHOICES)

    def clean_is_faculty(self):
        data = self.cleaned_data['is_faculty']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate whether you are faculty or a student.")
        return data

    def clean_institute(self):
        data = self.cleaned_data['institute']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate what institution you are affiliated with.")
        return data

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if data == '-----':
            raise forms.ValidationError("Please indicate your gender.")
        return data

    def clean_year_of_graduation(self):
        data = self.cleaned_data['year_of_graduation']
        if data == '-----':
            raise forms.ValidationError(
                "Please enter your year of graduation.")
        return data

    def clean_race(self):
        data = self.cleaned_data['race']
        if data == '-----':
            raise forms.ValidationError("Please indicate your race.")
        return data

    def clean_hispanic_latino(self):
        data = self.cleaned_data['hispanic_latino']
        if data == '-----':
            raise forms.ValidationError(
                "Please indicate if you are hispanic or latino.")
        return data

    def clean_age(self):
        data = self.cleaned_data['age']
        if data == '-----':
            raise forms.ValidationError("Please select an age.")
        return data

    def clean_specialty(self):
        data = self.cleaned_data['specialty']
        if data == '-----':
            raise forms.ValidationError("Please select a specialty.")
        return data

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()
        participant = cleaned_data.get("consent_participant")
        not_participant = cleaned_data.get("consent_not_participant")
        if participant and not_participant:
            # User should only select one field
            raise forms.ValidationError("You can be a participant or not, "
                                        "please select one or the other.")
        if not participant and not not_participant:
            # User should select at least one field
            raise forms.ValidationError("You must consent that you have read"
                                        " the document, whether you "
                                        "participate or not.")
        return cleaned_data


def user_created(sender, user, request, **kwargs):
    form = CreateAccountForm(request.POST)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
    profile.institute = form.data['institute']
    profile.consent_participant = request.POST.get('consent_participant',
                                                   False)
    profile.consent_not_participant = \
        request.POST.get('consent_not_participant', False)
    profile.is_faculty = form.data['is_faculty']
    profile.year_of_graduation = form.data['year_of_graduation']
    profile.specialty = form.data['specialty']
    profile.gender = form.data['gender']
    profile.hispanic_latino = form.data['hispanic_latino']
    profile.race = form.data['race']
    profile.age = form.data['age']
    profile.save()

user_registered.connect(user_created)


def clean_header(s):
    s = s.replace('<p>', '')
    s = s.replace('</p>', '')
    s = s.replace('</div>', '')
    s = s.replace('\n', '')
    s = s.replace('\r', '')
    s = s.replace('<', '')
    s = s.replace('>', '')
    s = s.replace('\'', '')
    s = s.replace('\"', '')
    s = s.replace(',', '')
    s = s.encode('utf-8')
    return s


class QuestionColumn(object):
    def __init__(self, hierarchy, question, answer=None):
        self.hierarchy = hierarchy
        self.question = question
        self.answer = answer
        self._submission_cache = Submission.objects.filter(
            quiz=self.question.quiz)
        self._response_cache = Response.objects.filter(
            question=self.question)
        self._answer_cache = self.question.answer_set.all()

    def question_id(self):
        return "%s_%s" % (self.hierarchy.id, self.question.id)

    def question_answer_id(self):
        return "%s_%s_%s" % (self.hierarchy.id,
                             self.question.id,
                             self.answer.id)

    def identifier(self):
        if self.question and self.answer:
            return self.question_answer_id()
        else:
            return self.question_id()

    def key_row(self):
        row = [self.question_id(),
               self.hierarchy.name,
               "Quiz",
               self.question.question_type,
               clean_header(self.question.text)]
        if self.answer:
            row.append(self.answer.id)
            row.append(clean_header(self.answer.label))
        return row

    def user_value(self, user):
        r = self._submission_cache.filter(user=user).order_by("-submitted")
        if r.count() == 0:
            # user has not submitted this form
            return ""
        submission = r[0]
        r = self._response_cache.filter(submission=submission)
        if r.count() > 0:
            if (self.question.is_short_text() or
                    self.question.is_long_text()):
                return r[0].value
            elif self.question.is_multiple_choice():
                if self.answer.value in [res.value for res in r]:
                    return self.answer.id
            else:  # single choice
                for a in self._answer_cache:
                    if a.value == r[0].value:
                        return a.id

        return ''

    @classmethod
    def all(cls, hrchy, section, key=True):
        columns = []
        ctype = ContentType.objects.get(app_label='quizblock', model='quiz')

        # quizzes
        for p in section.pageblock_set.filter(content_type=ctype):
            for q in p.block().question_set.all():
                if q.answerable() and (key or q.is_multiple_choice()):
                    # need to make a column for each answer
                    for a in q.answer_set.all():
                        columns.append(QuestionColumn(
                            hierarchy=hrchy, question=q, answer=a))
                else:
                    columns.append(QuestionColumn(hierarchy=hrchy, question=q))

        return columns
