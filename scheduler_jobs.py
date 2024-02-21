import sys
from datetime import date, timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from pytz import utc
from django.core import management
from django.core.management.commands import loaddata




####time date filter

def Hello():
    # print("Cron jobs running for sending emails.")
    # management.call_command('send_queued_mail')
    pass


def delete_last_30_days_mails():
    # print("Cron jobs running to delete 30 days old mails")
    # management.call_command('cleanup_mail --days=30 --delete-attachments')
    pass
