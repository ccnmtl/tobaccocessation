from tobaccocessation.activity_treatment_choice.views import *
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


from django.test.client import Client



class ViewTest(TestCase):  # unittest.


    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user('test_student', 'test@ccnmtl.com', 'testpassword')

    def tearDown(self):
        self.user.delete()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.c.get("/")
        self.assertEquals(response.status_code, 302)
    # def setUp(self):
    #     '''Set up method for testing views.'''
    #     self.factory = RequestFactory()
    #     self.user = User.objects.create_user('somestudent', 'email@email.com', 'somestudent')
    #     self.user.save()
    #     #IF BELOW VIEWS ARE COMMENTED OUT ALMOST EVERYTHING PASSES
    #     self.ecomap = Ecomap(pk='6', name="Test Map 1", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>somestudent</name><flashData><circles><circle><radius>499</radius></circle><circle><radius>350</radius></circle><circle><radius>200</radius></circle></circles><supportLevels><supportLevel><text>VeryHelpful</text></supportLevel><supportLevel><text>SomewhatHelpful</text></supportLevel><supportLevel><text>NotSoHelpful</text></supportLevel></supportLevels><supportTypes><supportType><text>Social</text></supportType><supportType><text>Advice</text></supportType><supportType><text>Empathy</text></supportType><supportType><text>Practical</text></supportType></supportTypes><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>")
    #     self.ecomap.owner = self.user
    #     self.ecomap.save()
    #     #unauthenticated user
    #     self.bad_user = User.objects.create_user('not_ecouser', 'email@email.com', 'not_ecouser')
    #     self.bad_user.save()
