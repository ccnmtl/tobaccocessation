import factory
from pagetree.tests.factories import UserFactory

from tobaccocessation.main.models import UserProfile


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    gender = 'M'
    is_faculty = 'ST'
    institute = 'I1'
    specialty = 'S1'
    hispanic_latino = 'Y'
    year_of_graduation = 2015
    consent_participant = True
    consent_not_participant = False
