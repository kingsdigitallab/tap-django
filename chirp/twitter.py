import logging

import requests
import simplejson
from django.conf import settings as s
from requests_oauthlib import OAuth1
from simplejson.errors import JSONDecodeError
from textblob import TextBlob

logger = logging.getLogger(__name__)


def harvest(f):
    collection = f.get_mongo_collection()
    if not collection:
        return

    _process_tweets(f, collection)


def _process_tweets(f, collection):
    tweets = tweet_generator(
        follow=f.follow, track=f.track, locations=f.locations)
    for t in tweets:
        # TODO: better way to check this
        f.refresh_from_db()
        if not f.active:
            break

        t['chirp'] = {}

        t = _add_sentiment_analysis_to_tweet(t)

        collection.insert(t)


def tweet_generator(follow='', track='', locations=''):
    url = s.TWITTER_API_URL
    auth = OAuth1(s.TWITTER_API_KEY, s.TWITTER_API_SECRET,
                  s.TWITTER_ACCESS_TOKEN,
                  s.TWITTER_ACCESS_TOKEN_SECRET)

    response = requests.post(url, auth=auth, stream=True, data={
        'follow': follow, 'track': track, 'locations': locations
    })

    if response.status_code != 200:
        logger.error('response status code {}'.format(response.status_code))
        return

    if response.encoding is None:
        response.encoding = 'utf-8'

    lines = response.iter_lines(decode_unicode=True)

    for line in lines:
        if line:
            try:
                yield simplejson.loads(line)
            except JSONDecodeError as e:
                logger.error('simplejson decode error')
                logger.error(e.args)


def _add_sentiment_analysis_to_tweet(tweet):
    if 'text' not in tweet:
        return tweet

    textblob = TextBlob(tweet['text'])
    sentiment = textblob.sentiment

    tweet['chirp']['sentiment'] = {}
    tweet['chirp']['sentiment']['polarity'] = sentiment.polarity
    tweet['chirp']['sentiment']['subjectivity'] = sentiment.subjectivity
    return tweet
