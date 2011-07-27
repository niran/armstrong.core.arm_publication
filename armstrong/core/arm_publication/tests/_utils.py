from armstrong.dev.tests.utils import ArmstrongTestCase
from armstrong.dev.tests.utils.concrete import *
from armstrong.dev.tests.utils.users import *

import fudge

from ..models import Publication


class ArmPublicationTestCase(ArmstrongTestCase):
    def setUp(self):
        Publication.objects.all().delete()
        Publication.objects.create(id=1, name='Armstrong Weekly')

    def tearDown(self):
        Publication.objects.all().delete()
