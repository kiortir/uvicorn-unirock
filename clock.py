from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from main import update_token
from worker import conn

q = Queue(connection=conn)

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=4)
def update_token():
    q.enqueue(update_token)
