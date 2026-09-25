from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import subprocess, os

# runs daily 18:00 IST (12:30 UTC) - covers Tue/Wed/Thu + any day
# checks if event today -> if livestream -> capture -> process

from event_check import has_event_today
def job():
    print(f"[{datetime.now()}] checking for today's event...")
    has_event = has_event_today()
    is_live = False # set LIVE_STREAM_URL env to enable yt check
    if has_event and is_live:
        subprocess.run(["python","src/pipeline.py"], check=False)
    else:
        print("no event/livestream today, skipping")

if __name__=="__main__":
    sched=BlockingScheduler(timezone="Asia/Kolkata")
    sched.add_job(job, 'cron', hour=18, minute=0)
    # also run once on start for testing
    print("scheduler started, next run 18:00 IST daily")
    sched.start()
