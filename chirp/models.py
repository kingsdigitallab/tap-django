from django.conf import settings as s
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from pymongo import MongoClient
from bson.code import Code

from . import aggregations


class User(AbstractUser):
    pass


class AggregationFramework(PolymorphicModel):
    label = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


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
            '{}_{}'.format(f.uid, slugify(self.label)),
            query=self.query)

        return list(result.find())


class Filter(models.Model):
    active = models.BooleanField(help_text='Set active to harvest tweets.')
    label = models.CharField(max_length=64, unique=True)
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
        return self.label

    @property
    def uid(self):
        return '{}_{}_{}'.format(
            self._meta.app_label, self.__class__.__name__, self.id).lower()

    def get_mongo_collection(self):
        client = MongoClient(s.MONGO_DB_URI)
        db = client[s.MONGO_DB_NAME]
        collection = db[self.uid]
        return collection

    @property
    def number_of_tweets(self):
        collection = self.get_mongo_collection()
        return collection.count()

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

    def get_sentiment_count(self):
        collection = self.get_mongo_collection()
        options = aggregations.sentiment_count_mr

        r = collection.map_reduce(
            options['mapper'], options['reducer'],
            '{}_sentiment_count'.format(self.uid))

        return list(r.find())

    def get_sentiment_by_country(self):
        collection = self.get_mongo_collection()
        options = aggregations.sentiment_country_mr

        r = collection.map_reduce(
            options['mapper'], options['reducer'],
            '{}_sentiment_country'.format(self.uid), query=options['query'])

        return list(r.find())

    def get_sentiment_by_date(self):
        collection = self.get_mongo_collection()
        options = aggregations.sentiment_date_mr

        r = collection.map_reduce(
            options['mapper'], options['reducer'],
            '{}_sentiment_date'.format(self.uid), query=options['query'])

        return list(r.find())

    def get_tweets_total_by_country(self):
        collection = self.get_mongo_collection()
        options = aggregations.tweets_total_country_mr

        r = collection.map_reduce(
            options['mapper'], options['reducer'],
            '{}_tweets_total_country'.format(self.uid), query=options['query'])
        return list(r.find())
