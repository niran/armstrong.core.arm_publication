import datetime

from django.db import models

from ...mixins import PublicationFields
from ...models import Publication, PublicationNode


class ContentManager(models.Manager):
    def create_published(self, publication=None, **content_kwargs):
        if publication is None:
            publication = Publication.objects.default
        object = self.create(**content_kwargs)
        PublicationNode.objects.create(content=object, publication=publication,
            pub_date=datetime.datetime.now())
        return object


class Story(PublicationFields, models.Model):
    body = models.TextField(default='')

    objects = ContentManager()
