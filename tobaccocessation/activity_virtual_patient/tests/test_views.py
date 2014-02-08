# flake8: noqa
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from pagetree.models import Hierarchy
from tobaccocessation.activity_virtual_patient.models import \
    ConcentrationChoice, TreatmentClassification, ActivityState, \
    DosageChoice, Medication, Patient, TreatmentFeedback, TreatmentOption
from tobaccocessation.main.models import UserProfile
import json


# class TestViews(TestCase):
#     def setUp(self):
#         self.u = User.objects.create(username="testuser")
#         self.u.set_password("test")
#         self.u.save()
#         UserProfile.objects.create(user=self.u,
#                                    gender='M',
#                                    is_faculty='ST',
#                                    institute='I1',
#                                    specialty='S1',
#                                    hispanic_latino='Y',
#                                    year_of_graduation=2015,
#                                    consent=True)
#         self.c = Client()
#         self.c.login(username="testuser", password="test")
# 
#     def test_root(self):
#         Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         r = self.c.get("/pages/main/assist/activity-virtual-patient/")
#         self.assertEqual(r.status_code, 302)
# 
#     def test_save(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         r = self.c.post(
#             "/activity/virtualpatient/save/%d/" % p.id,
#             dict(json="{}"))
#         self.assertEqual(r.status_code, 200)
# 
#     def test_save_empty_json(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         r = self.c.post(
#             "/activity/virtualpatient/save/%d/" % p.id,
#             dict(json=""))
#         self.assertEqual(r.status_code, 200)
# 
#     def test_reset(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         r = self.c.post(
#             "/activity/virtualpatient/save/%d/" % p.id,
#             dict(json="{}"))
#         self.assertEqual(r.status_code, 200)
#         r = self.c.post(
#             "/activity/virtualpatient/reset/%d/" % p.id,
#             dict(json="{}"))
#         self.assertEqual(r.status_code, 302)
# 
#     def test_options(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         h = Hierarchy.objects.create(name="main", base_url="/")
#         h.get_root().add_child_section_from_dict(
#             {
#                 'label': 'Assist',
#                 'slug': 'assist',
#                 'pageblocks': [],
#                 'children': [
#                     {'label': 'activity virtual patient',
#                      'slug': 'activity-virtual-patient',
#                      'pageblocks': [],
#                      'children': []},
#                 ],
#             }
#         )
#         r = self.c.get(
#             "/pages/main/assist/activity-virtual-patient/options/%d/" % p.id)
#         self.assertEqual(r.status_code, 200)
# 
#     def test_selection(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         h = Hierarchy.objects.create(name="main", base_url="/")
#         h.get_root().add_child_section_from_dict(
#             {
#                 'label': 'Assist',
#                 'slug': 'assist',
#                 'pageblocks': [],
#                 'children': [
#                     {'label': 'activity virtual patient',
#                      'slug': 'activity-virtual-patient',
#                      'pageblocks': [],
#                      'children': []},
#                 ],
#             }
#         )
#         d = dict(patients={str(p.id): dict(results=[3, 4, 5])})
#         ActivityState.objects.create(user=self.u, json=json.dumps(d))
#         r = self.c.get(
#             "/pages/main/assist/activity-virtual-patient/selection/%d/" % p.id)
#         self.assertEqual(r.status_code, 200)
# 
#     def test_prescription(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         h = Hierarchy.objects.create(name="main", base_url="/")
#         h.get_root().add_child_section_from_dict(
#             {
#                 'label': 'Assist',
#                 'slug': 'assist',
#                 'pageblocks': [],
#                 'children': [
#                     {'label': 'activity virtual patient',
#                      'slug': 'activity-virtual-patient',
#                      'pageblocks': [],
#                      'children': []},
#                 ],
#             }
#         )
#         d = dict(patients={str(p.id): dict(results=[3, 4, 5],
#                                            prescribe='foo')})
#         ActivityState.objects.create(user=self.u, json=json.dumps(d))
#         r = self.c.get(
#             "/pages/main/assist/activity-virtual-patient/prescription/%d/" %
#             p.id)
#         self.assertEqual(r.status_code, 200)
# 
#     def test_results(self):
#         p = Patient.objects.create(
#             name="foo",
#             description="bar",
#             history="history",
#             display_order=1)
#         h = Hierarchy.objects.create(name="main", base_url="/")
#         h.get_root().add_child_section_from_dict(
#             {
#                 'label': 'Assist',
#                 'slug': 'assist',
#                 'pageblocks': [],
#                 'children': [
#                     {'label': 'activity virtual patient',
#                      'slug': 'activity-virtual-patient',
#                      'pageblocks': [],
#                      'children': []},
#                 ],
#             }
#         )
#         m1 = Medication.objects.create(
#             name="foo",
#             instructions="instructions",
#             display_order=1,
#             tag="foo")
#         Medication.objects.create(
#             name="bar",
#             instructions="instructions",
#             display_order=2,
#             tag="bar")
#         tc = TreatmentClassification.objects.create(rank=1, description="foo")
#         TreatmentOption.objects.create(
#             patient=p, classification=tc, medication_one=m1,
#             medication_two=None)
#         cc1 = ConcentrationChoice.objects.create(
#             medication=m1, concentration="c", correct=True, display_order=1)
#         dc1 = DosageChoice.objects.create(medication=m1, dosage="all of it",
#                                           correct=True, display_order=1)
#         d = dict(patients={str(p.id): dict(results=[3, 4, 5], prescribe='foo',
#                                            foo=dict(concentration=cc1.id,
#                                                     dosage=dc1.id))})
#         TreatmentFeedback.objects.create(
#             patient=p, classification=tc, feedback="ok",
#             correct_dosage=True)
#         ActivityState.objects.create(user=self.u, json=json.dumps(d))
#         r = self.c.get(
#             "/pages/main/assist/activity-virtual-patient/results/%d/" % p.id)
#         self.assertEqual(r.status_code, 200)
