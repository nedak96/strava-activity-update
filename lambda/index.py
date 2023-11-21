import logging
from datetime import datetime, time

import strava_auth
import stravalib
from aws_lambda_typing import context as context_
from aws_lambda_typing import events
from garmin_client import GarminClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(_: events.EventBridgeEvent, context: context_.Context) -> None:
  logger.info("Starting lambda: %s", context.function_name)

  garmin_client = GarminClient()
  strava_client = stravalib.Client()
  strava_auth.authenticate_strava(strava_client)

  logger.info("Fetching Strava activities")
  try:
    strava_activities = strava_client.get_activities(
      after=datetime.combine(datetime.now(), time.min)
    )
  except Exception as e:
    logger.error("Error fetching Strava activities: %s", e)
    raise e

  strava_activity_ids = {a.external_id for a in strava_activities}

  for activity in garmin_client.get_activities():
    if activity.activity_id not in strava_activity_ids:
      with garmin_client.get_fit_data(activity.activity_id) as fit_data:
        logging.info("Uploading activity to Strava: %s", activity.activity_id)
        try:
          strava_client.upload_activity(
            fit_data,
            data_type="fit",
            external_id=activity.activity_id,
          ).wait()
        except Exception as e:
          logger.error("Error uploading activity: %s", e)
          raise e
