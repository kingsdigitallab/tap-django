from bson.code import Code
from django.conf import settings as s
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from pymongo import DESCENDING, MongoClient

from . import aggregations
from .fields import JavaScriptField


class User(AbstractUser):
    twitter_api_key = models.CharField(max_length=64)
    twitter_api_secret = models.CharField(max_length=64)
    twitter_access_token = models.CharField(max_length=64)
    twitter_access_token_secret = models.CharField(max_length=64)

    @property
    def has_twitter_credentials(self):
        credentials = '{}{}{}{}'.format(
            self.twitter_api_key, self.twitter_api_secret,
            self.twitter_access_token, self.twitter_access_token_secret)

        if credentials:
            return True

        return False


class AggregationFramework(PolymorphicModel):
    title = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=128)
    query_field = models.CharField(
        max_length=128, blank=True, null=True,
        help_text='The name of the field used to drill-down results')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Aggregation'
        verbose_name_plural = 'Aggregations'

    def __str__(self):
        return self.title

    def perform(self, f, query=None):
        pass

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Aggregation(AggregationFramework):
    pipeline_js = JSONField()

    class Meta:
        verbose_name = 'Aggregation'

    def perform(self, f, query=None):
        collection = f.get_mongo_collection()
        pipeline = self.pipeline_js

        if query:
            if '$match' not in pipeline[0]:
                pipeline.insert(0, {'$match': {}})

            for k in query.keys():
                pipeline[0]['$match'][k] = query[k]

        result = collection.aggregate(pipeline)

        return list(result)


class MapReduce(AggregationFramework):
    mapper_js = JavaScriptField(blank=True, null=True)
    reducer_js = JavaScriptField(blank=True, null=True)
    query_js = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Map/Reduce'
        verbose_name_plural = 'Mappers/Reducers'

    def perform(self, f, query=None):
        collection = f.get_mongo_collection()

        if query:
            query = {'$and': [self.query_js, query]}
        else:
            query = self.query_js

        result = collection.map_reduce(
            Code(self.mapper_js), Code(self.reducer_js),
            '{}_{}'.format(f.uid, slugify(self.title)),
            query=query)

        return list(result.find())


class Filter(models.Model):
    active = models.BooleanField(
        help_text=('Set active to harvest tweets.'
                   'You need to have twitter credentials in your account '
                   'to be able to harvest tweets.')
    )
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

    sentiment_threshold = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0,
        validators=[MaxValueValidator(1.0), MinValueValidator(-1.0)],
        help_text=('Minimum value (-1.0 to 1.0) used to label tweets '
                   'with positive/negative sentiment.'))

    aggregations = models.ManyToManyField(
        AggregationFramework, related_name='filters')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        if not self.follow and not self.track and not self.locations:
            raise ValidationError(_(
                'Fill at least one of follow, track, or locations'))

        if self.active and not self.user.has_twitter_credentials:
            raise ValidationError(_(
                'Set you twitter credentials before activating a filter'))

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

        if r:
            return r[0]['sentiment_avg']

        return 0

    def get_aggregations(self):
        return self.aggregations.all().order_by('title')

    def get_tweets(self, query=None, page=1):
        collection = self.get_mongo_collection()
        cursor = collection.find(
            filter=query, sort=[('timestamp_ms', DESCENDING)], limit=20)

        return cursor

    def get_words(self, query=None):
        collection = self.get_mongo_collection()
        mapper_js = Code("""function() {
            for (var w in this.chirp.words) {
                emit(this.chirp.words[w], 1);
            }
        }""")
        reducer_js = Code("""function(key, values) {
            return Array.sum(values);
        }""")
        result = collection.map_reduce(
            mapper_js, reducer_js,
            '{}_{}'.format(self.uid, slugify(self.title)),
            query=query)
        total_words = result.count()

        words = [[item['_id'], item['value']]
                 for item in list(result.find())
                 if item['value'] / total_words > 0.025]
        return words
