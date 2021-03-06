import rules

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django_extensions.db.models import TimeStampedModel


class Community(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    subscribers = models.ManyToManyField('auth.User', through='CommunitySubscription', related_name='communities')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('community_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('community_update', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['name']


@rules.predicate
def can_edit_community(user, community):
    try:
        return community.community_subscriptions.get(user=user).role == CommunitySubscription.ROLE_OWNER
    except CommunitySubscription.DoesNotExist:
        return False

rules.add_perm('community.can_edit', can_edit_community)


class CommunitySubscription(TimeStampedModel):
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_SUBSCRIBER = 'subscriber'
    ROLE_CHOICES = (
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_SUBSCRIBER, 'Subscriber'),
    )

    community = models.ForeignKey(Community, related_name='community_subscriptions')
    user = models.ForeignKey('auth.User', related_name='community_subscriptions')
    role = models.CharField(max_length=64, choices=ROLE_CHOICES)

    class Meta:
        ordering = ['user']
        unique_together = (
            ('community', 'user'),
        )
