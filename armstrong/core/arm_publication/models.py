import datetime

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

PUBLICATION_CACHE = {}

class PublicationManager(models.Manager):
    """
    The default manager for Publication objects.

    Provides a `get_default` method for retrieving a cached instance of the 
    publication object configured by the `DEFAULT_PUBLICATION_ID` setting.
    """

    def get_default(self):
        try:
            publication_id = settings.DEFAULT_PUBLICATION_ID
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                "The DEFAULT_PUBLICATION_ID setting must be provided " + \
                "when using the publications framework.")
        try:
            default_publication = PUBLICATION_CACHE[publication_id]
        except KeyError:
            default_publication = self.get(pk=publication_id)
            PUBLICATION_CACHE[publication_id] = default_publication
        return default_publication

    @property
    def default(self):
        return self.get_default()

    def clear_cache(self):
        global PUBLICATION_CACHE
        PUBLICATION_CACHE = {}


class Publication(MPTTModel):
    """
    A model for grouping content and content access by named publications.
    """

    objects = PublicationManager()

    name = models.CharField(_('name'), max_length=50, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = _('publication')
        verbose_name_plural = _('publications')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Publication, self).save(*args, **kwargs)
        if self.id in PUBLICATION_CACHE:
            del PUBLICATION_CACHE[self.id]

    def delete(self):
        pk = self.pk
        super(Publication, self).delete()
        try:
            del PUBLICATION_CACHE[pk]
        except KeyError:
            pass


class PublicationNode(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'object_id')
    publication = models.ForeignKey(Publication, verbose_name=_("publication"))
    pub_date = models.DateTimeField(_('publication date'))

    class Meta:
        unique_together = ('object_id', 'content_type', 'publication')

    def __unicode__(self):
        return u"%s - %s" % (self.publication, self.content)
