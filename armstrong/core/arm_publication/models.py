import datetime

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class PublicationManager(models.Manager):
    """
    The default manager for Publication objects.

    Provides a `get_default` method for retrieving a cached instance of the 
    publication object configured by the `DEFAULT_PUBLICATION_ID` setting.
    """

    def get_default(self):
        """Returns the default Publication.

        Either the sole Publication or the Publication referenced by
        The default Publication is either the one specified by
        ARMSTRONG_DEFAULT_PUBLICATION_ID or the only Publication in the
        database. If neither situation applies, an error will be raised.
        """
        try:
            publication_id = settings.ARMSTRONG_DEFAULT_PUBLICATION_ID
            return self.get(pk=publication_id)
        except AttributeError:
            pass

        if Publication.objects.count() == 1:
            return Publication.objects.all()[0]

        if Publication.objects.count() == 0:
            raise Publication.DoesNotExist

        raise ImproperlyConfigured(
            "The ARMSTRONG_DEFAULT_PUBLICATION_ID setting must be provided "
            "when using the publications framework.")

    @property
    def default(self):
        if not hasattr(self, '_default'):
            self._default = self.get_default()
        return self._default

    def _clear_default_cache(self):
        if hasattr(self, '_default'):
            del self._default


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
        Publication.objects._clear_default_cache()
        return super(Publication, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Publication.objects._clear_default_cache()
        return super(Publication, self).delete(*args, **kwargs)


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
