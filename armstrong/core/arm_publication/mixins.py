from django.db import models

from .models import Publication, PublicationNode


class PublicationFields(models.Model):
    publications = models.ManyToManyField(Publication, through=PublicationNode)

    class Meta:
        abstract = True

    @property
    def pub_date(self):
        # for backwards compatibility
        qs = self.publicationnode_set.order_by('pub_date')
        return qs[0].pub_date if qs else None

    @property
    def publication(self):
        # for backwards compatibility
        qs = self.publicationnode_set.order_by('pub_date')
        return qs[0].publication if qs else None
