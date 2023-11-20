import logging
from datetime import datetime, timedelta

import strava_auth
import stravalib
from aws_lambda_typing import context as context_
from aws_lambda_typing import events

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(_: events.EventBridgeEvent, context: context_.Context) -> None:
    logger.info("Starting lambda: %s", context.function_name)

    strava_client = stravalib.Client()
    strava_auth.authenticate_strava(strava_client)
    activities = strava_client.get_activities(
        after=datetime.now() - timedelta(seconds=60)
    )

    for activity in activities:
        if activity.sport_type == "Run":
            if activity.private:
                logger.info("Set activity to public: %s", activity.id)
                try:
                    strava_client.update_activity(
                        activity_id=activity.id, private=False
                    )
                except Exception as e:
                    logger.error("Error updating activity")
                    raise e
        else:
            logger.info("Delete activity: %s", activity.id)
            try:
                logger.info("Skip")
                # strava_client.delete_activity(activity_id=activity.id)
            except Exception as e:
                logger.error("Error updating activity")
                raise e
