import logging
import re
import string

import requests
import simplejson
from django.conf import settings as s
from nltk.corpus import stopwords
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
    if not f.user.has_twitter_credentials:
        return

    tweets = tweet_generator(
        f.user, follow=f.follow, track=f.track, locations=f.locations)
    for t in tweets:
        # TODO: better way to check this
        f.refresh_from_db()
        if not f.active:
            break

        t['chirp'] = {}

        t = _add_npl_to_tweet(t, f.sentiment_threshold)

        if not collection.find_one({'id_str': t['id_str']}):
            collection.insert(t)


def tweet_generator(user, follow='', track='', locations=''):
    url = s.TWITTER_API_URL
    auth = OAuth1(user.twitter_api_key, user.twitter_api_secret,
                  user.twitter_access_token,
                  user.twitter_access_token_secret)

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


def _add_npl_to_tweet(tweet, sentiment_threshold):
    tweet = add_sentiment_to_tweet(tweet, sentiment_threshold)
    tweet = add_words_to_tweet(tweet)

    return tweet


def add_sentiment_to_tweet(tweet, sentiment_threshold):
    text = get_text_from_tweet(tweet)

    if not text:
        return tweet

    sentiment = _get_sentiment_from_tweet_text(text)

    if sentiment:
        polarity = sentiment.polarity

        tweet['chirp']['sentiment'] = {}
        tweet['chirp']['sentiment']['polarity'] = polarity
        tweet['chirp']['sentiment']['subjectivity'] = sentiment.subjectivity

        label = 'neutral'
        if polarity > sentiment_threshold:
            label = 'positive'
        elif polarity < sentiment_threshold:
            label = 'negative'

        tweet['chirp']['sentiment']['label'] = label

    return tweet


def get_text_from_tweet(tweet):
    if 'text' not in tweet:
        return None

    if 'extended_tweet' in tweet:
        return tweet['extended_tweet']['full_text']

    if 'retweeted_status' in tweet:
        if 'extended_tweet' in tweet['retweeted_status']:
            return tweet['retweeted_status']['extended_tweet']['full_text']
        else:
            return tweet['retweeted_status']['text']

    return tweet['text']


def _get_sentiment_from_tweet_text(text):
    textblob = TextBlob(text)
    return textblob.sentiment


def add_words_to_tweet(tweet):
    text = get_text_from_tweet(tweet)

    if not text:
        return tweet

    words = _get_words_from_tweet_text(text)

    if words:
        tweet['chirp']['words'] = words

    return tweet


def _get_words_from_tweet_text(text):
    tokens = _tokenize(text)

    words = [
        token if _is_emoticon(token) else _get_lemma(token)
        for token in tokens
        if _is_valid_token(token)
    ]

    return words


emoticon_str = r"""(?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
emoticon_re = re.compile(r'^{}$'.format(emoticon_str),
                         re.VERBOSE | re.IGNORECASE)


tokens_str = [
    emoticon_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    # URLs
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # noqa
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]
tokens_re = re.compile(r'({})'.format('|'.join(tokens_str)),
                       re.VERBOSE | re.IGNORECASE)


def _tokenize(text):
    return tokens_re.findall(text)


def _is_emoticon(token):
    if emoticon_re.search(token):
        return True

    return False


def _get_lemma(token):
    # lemmatisation is not working properly, turning it off for now
    # return Word(token.lower()).lemmatize()
    return token.lower()


stop = stopwords.words('english')
stop.append('amp')

punctuation = string.punctuation
punctuation = '{}’“”…'.format(punctuation)


def _is_valid_token(token):
    if not token:
        return False

    token = token.lower()

    if token in stop:
        return False
    if token in punctuation:
        return False
    return True
