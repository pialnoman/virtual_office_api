# ========================================
# Scheduler Jobs
# ========================================
import time

from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import scheduler_jobs
scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)

# jobs
scheduler.add_job(scheduler_jobs.Hello, 'interval', seconds=3)
scheduler.add_job(scheduler_jobs.delete_last_30_days_mails, 'interval', days=30)
scheduler.start()

# ===========================================
