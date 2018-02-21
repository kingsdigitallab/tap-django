from bson.code import Code
from django.conf import settings as s
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from pymongo import MongoClient

from . import aggregations


class User(AbstractUser):
    pass


class AggregationFramework(PolymorphicModel):
    title = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


@receiver(pre_save, sender=AggregationFramework)
def aggregation_pre_save(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)


class Aggregation(AggregationFramework):
    pipeline = JSONField()

    def perform(self, f):
        collection = f.get_mongo_collection()
        result = collection.aggregate(self.pipeline)

        return list(result)


class MapReduce(AggregationFramework):
    mapper = models.TextField(help_text='Enter valid JavaScript')
    reducer = models.TextField(help_text='Enter valid JavaScript')
    query = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Map/Reduce'
        verbose_name_plural = 'Mappers/Reducers'

    def perform(self, f):
        collection = f.get_mongo_collection()

        result = collection.map_reduce(
            Code(self.mapper), Code(self.reducer),
            '{}_{}'.format(f.uid, slugify(self.title)),
            query=self.query)

        return list(result.find())


class Filter(models.Model):
    active = models.BooleanField(help_text='Set active to harvest tweets.')
    title = models.CharField(max_length=64, unique=True)
    follow = models.CharField(
        max_length=64, blank=True, null=True,
        help_text=('A comma separated list of user IDs, indicating the users '
                   'to return statuses for in the stream.')
    )
    track = models.CharField(
        max_length=256, blank=True, null=True,
        help_text=('Keywords to track. Phrases of keywords are specified by '
                   'a comma-separated list.')
    )
    locations = models.TextField(
        blank=True, null=True,
        help_text=('Sets of bounding boxes to track. '
                   'One bounding box per line.')
    )

    aggregations = models.ManyToManyField(
        AggregationFramework, related_name='filters')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def uid(self):
        return '{}_{}_{}'.format(
            self._meta.app_label, self.__class__.__name__, self.id).lower()

    @property
    def number_of_tweets(self):
        collection = self.get_mongo_collection()
        return collection.count()

    def get_mongo_collection(self):
        client = MongoClient(s.MONGO_DB_URI)
        db = client[s.MONGO_DB_NAME]
        collection = db[self.uid]
        return collection

    @property
    def sentiment(self):
        s = self.sentiment_avg

        if (s > 0):
            return 'positive'
        elif s < 0:
            return 'negative'

        return 'neutral'

    @property
    def sentiment_avg(self):
        collection = self.get_mongo_collection()
        r = list(collection.aggregate(aggregations.sentiment_avg))

        return r[0]['sentiment_avg']

    def get_aggregations(self):
        return self.aggregations.all()
