import logging

from aws_lambda_typing import context as context_
from aws_lambda_typing import events

from .garmin_client import GarminClient
from .strava_client import StravaClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(_: events.EventBridgeEvent, context: context_.Context) -> None:
  logger.info("Starting lambda: %s", context.function_name)

  garmin_client = GarminClient()
  activities = garmin_client.get_activities()
  if not activities:
    return

  strava_client = StravaClient()
  strava_activity_ids = strava_client.get_activity_external_ids()
  for activity in activities:
    if f"{activity.activity_id}.fit" not in strava_activity_ids:
      with garmin_client.get_fit_data(activity.activity_id) as fit_data:
        strava_client.upload_activity(fit_data, activity.activity_id)
