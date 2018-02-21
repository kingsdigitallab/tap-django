from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

register_events(scheduler)
scheduler.start()
