from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.jobstores.base import JobLookupError

from .twitter import harvest
from django.db.models.signals import post_save
from django.dispatch import receiver

from chirp.models import Filter

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

register_events(scheduler)
scheduler.start()


@receiver(post_save, sender=Filter, dispatch_uid="add_remove_job")
def add_remove_jobs(sender, instance, **kwargs):
    print("post_save")
    if instance.active:
            if instance.user.has_twitter_credentials:
                scheduler.add_job(harvest, 'interval',
                                  args=[instance],
                                  id=instance.uid,
                                  minutes=1, max_instances=1,
                                  replace_existing=True)
    else:
        try:
            scheduler.remove_job(instance.uid)
        except JobLookupError:
            pass
