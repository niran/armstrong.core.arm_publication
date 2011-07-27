import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.utils.unittest import skip

from .arm_publication_support.models import Story
from ._utils import ArmPublicationTestCase
from ..models import Publication, PublicationNode


class TestPublications(ArmPublicationTestCase):
    def test_publication_manager(self):
        p = Publication.objects.get_default()
        self.assertTrue(isinstance(p, Publication))
        p.delete()
        self.assertRaises(Publication.DoesNotExist,
                          Publication.objects.get_default)


class TestPublicationsBasicMPTT(ArmPublicationTestCase):
    def test_parent_child_relationship(self):
        with self.settings(ARMSTRONG_DEFAULT_PUBLICATION_ID=1):
            p = Publication.objects.default
            child = Publication.objects.create(name='Hello Kitty Weekly')
            child.move_to(p)
            self.assertEqual(child.parent, p)
            self.assertEqual(child.get_ancestors()[0], p)
            child = Publication.objects.create(name='GI Joe International')
            child.move_to(p)
            Publication.objects._clear_default_cache()   # XXX
            p = Publication.objects.default  # XXX
            self.assertEqual(p.get_descendant_count(), 2)
            self.assertEqual(p.get_children().count(), 2)
            self.assertEqual(p.children.count(), 2)

    def test_sibling_relationship(self):
        with self.settings(ARMSTRONG_DEFAULT_PUBLICATION_ID=1):
            p = Publication.objects.default
            child1 = Publication.objects.create(name='Hello Kitty Weekly')
            child1.move_to(p)
            self.assertFalse(child1.get_siblings())
            child2 = Publication.objects.create(name='GI Joe International')
            child2.move_to(p)
            self.assertEqual(child1.get_siblings()[0], child2)

    def test_grandkids(self):
        with self.settings(ARMSTRONG_DEFAULT_PUBLICATION_ID=1):
            p = Publication.objects.default
            child = Publication.objects.create(name='Hello Kitty Weekly')
            child.move_to(p)
            Publication.objects._clear_default_cache()   # XXX
            p = Publication.objects.default   # XXX
            self.assertEqual(child.parent, p)
            grandkid = Publication.objects.create(name='GI Joe International')
            grandkid.move_to(child)
            Publication.objects._clear_default_cache()   # XXX
            p = Publication.objects.default   # XXX
            self.assertEqual(p.get_children()[0], child)
            self.assertEqual(p.get_descendant_count(), 2)


class TestPublicationMPTTQuerySets(ArmPublicationTestCase):
    def setUp(self):
        super(TestPublicationMPTTQuerySets, self).setUp()
        with self.settings(ARMSTRONG_DEFAULT_PUBLICATION_ID=1):
            p = Publication.objects.default
            self.child_pub = Publication.objects.create(name='Hello Kitty Weekly')
            p.children.add(self.child_pub)
            self.test_story = Story.objects.create_published(
                publication=self.child_pub)
            self.parent_pub = p

    @skip("Publications can't query their content yet")
    def test_parent_qs_contains_child(self):
        self.assertTrue(self.child_pub.content_set.\
            filter(pk=self.test_story.pk))
        self.assertFalse(self.parent_pub.content_set.\
            filter(pk=self.test_story.pk))
        self.assertTrue(self.parent_pub.content_set_full.\
            filter(pk=self.test_story.pk))


class TestPublicationNode(ArmPublicationTestCase):
    def test_unique_constraint(self):
        content = Story.objects.create_published()
        self.assertRaises(IntegrityError, PublicationNode.objects.create, **{
            'pub_date': datetime.datetime.now(),
            'content_type': ContentType.objects.get_for_model(content),
            'object_id': content.pk,
            'publication': Publication.objects.default,
        })
