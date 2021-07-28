import requests
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=4)
def update_token():
    requests.post('https://uvicorn-unirock-api.herokuapp.com/reload-tokens')
