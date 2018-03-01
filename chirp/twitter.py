import logging
import re
import string

import requests
import simplejson
from django.conf import settings as s
from nltk.corpus import stopwords
from requests_oauthlib import OAuth1
from simplejson.errors import JSONDecodeError
from textblob import TextBlob, Word

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

        t = _add_npl_to_tweet(t)

        if not collection.find_one({'id_str': t['id_str']}):
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


def _add_npl_to_tweet(tweet):
    text = get_text_from_tweet(tweet)

    if not text:
        return tweet

    sentiment = get_sentiment_from_tweet_text(text)

    if sentiment:
        tweet['chirp']['sentiment'] = {}
        tweet['chirp']['sentiment']['polarity'] = sentiment.polarity
        tweet['chirp']['sentiment']['subjectivity'] = sentiment.subjectivity

    words = get_words_from_tweet_text(text)

    if words:
        tweet['chirp']['words'] = words

    return tweet


def get_text_from_tweet(tweet):
    if 'text' not in tweet:
        return None

    text = tweet['text']

    if 'retweeted_status' in tweet:
        if 'extended_tweet' in tweet['retweeted_status']:
            text = tweet['retweeted_status']['extended_tweet']['full_text']
        else:
            text = tweet['retweeted_status']['text']

    return text


def get_sentiment_from_tweet_text(text):
    textblob = TextBlob(text)
    return textblob.sentiment


def get_words_from_tweet_text(text):
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
    return Word(token.lower()).lemmatize()


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
