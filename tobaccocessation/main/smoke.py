from smoketest import SmokeTest
from .models import UserProfile


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = UserProfile.objects.all().count()
        self.assertTrue(cnt > 0)
