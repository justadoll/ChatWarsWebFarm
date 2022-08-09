import logging

from django.conf import settings
from main.models import CW_players
from main.chw_manager import ChwMaster
import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

import asyncio
logger = settings.LOGGER

chw_master = ChwMaster(api_id=settings.API_ID, api_hash=settings.API_HASH)

def my_job():
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  all_players = CW_players.objects.all()
  for player in all_players:
    #group1 = await asyncio.gather(*[mng.sender(session_info, "", "/start") for session_info in full[0:25]])
    async_result = loop.run_until_complete(chw_master.send_report(player_obj=player))
    logger.debug(f"{async_result=}")
  logger.info("JOB FINISHED!")


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
  help = "Runs APScheduler."

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
      my_job,
      trigger=CronTrigger(hour="09",minute="10"),
      id="morning_send_report_job",
      max_instances=10,
      replace_existing=True,
      misfire_grace_time=120,
    )

    scheduler.add_job(
      my_job,
      trigger=CronTrigger(hour="17", minute="10"),
      id="afternoon_send_report_job",
      max_instances=10,
      replace_existing=True,
      misfire_grace_time=120,
    )

    scheduler.add_job(
      my_job,
      trigger=CronTrigger(hour="01", minute="10"),
      id="evening_send_report_job",
      max_instances=10,
      replace_existing=True,
      misfire_grace_time=120,
    )

    logger.info("Added 'send_report' jobs")

    scheduler.add_job(
      delete_old_job_executions,
      trigger=CronTrigger(
        day_of_week="mon", hour="00", minute="00"
      ),  # Midnight on Monday, before start of the next work week.
      id="delete_old_job_executions",
      max_instances=1,
      replace_existing=True,
    )
    logger.info(
      "Added weekly job: 'delete_old_job_executions'."
    )

    try:
      logger.info("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      logger.info("Stopping scheduler...")
      scheduler.shutdown()
      logger.info("Scheduler shut down successfully!")
