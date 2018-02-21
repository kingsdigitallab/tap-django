from django.test import TestCase

from .twitter import tweet_generator


class TwitterTest(TestCase):
    def test_tweet_generator(self):
        tweets = tweet_generator(track='@twitter')
        for t in tweets:
            self.assertTrue('text' in t)
            break
