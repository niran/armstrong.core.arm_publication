from django.contrib.contenttypes import generic
from django.db import models

from .models import Publication, PublicationNode


class PublicationMixin(models.Model):
    publication_nodes = generic.GenericRelation(PublicationNode)

    class Meta:
        abstract = True

    @property
    def pub_date(self):
        # for backwards compatibility
        qs = self.publication_nodes.order_by('pub_date')
        return qs[0].pub_date if qs else None

    @property
    def publication(self):
        # for backwards compatibility
        qs = self.publication_nodes.order_by('pub_date')
        return qs[0].publication if qs else None
