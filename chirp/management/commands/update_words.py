from chirp.models import Filter
from chirp.twitter import add_words_to_tweet
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Updates the words field for tweets from the given Filter'

    def add_arguments(self, parser):
        parser.add_argument('filter_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for filter_id in options['filter_id']:
            try:
                f = Filter.objects.get(pk=filter_id)
            except Filter.DoesNotExist:
                raise CommandError(
                    'Filter "{}" does not exist'.format(filter_id))

            self.stdout.write(self.style.SUCCESS(
                'Updating documents from filter {}...'.format(f.title)))

            count = self._update_words(f)

            self.stdout.write(self.style.SUCCESS(
                'Updated {} documents'.format(count)))

    def _update_words(self, f):
        count = 0
        collection = f.get_mongo_collection()
        cursor = collection.find()

        for tweet in cursor:
            tweet = add_words_to_tweet(tweet)

            if 'chirp' not in tweet:
                continue
            if 'words' not in tweet['chirp']:
                continue

            result = collection.update_one(
                {'_id': tweet['_id']}, {
                    '$set': {'chirp.words': tweet['chirp']['words']}
                })
            count = count + result.modified_count

        return count
