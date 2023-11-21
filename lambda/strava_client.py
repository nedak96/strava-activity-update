import logging
import time as epochtime
from datetime import datetime, time
from io import BufferedReader
from typing import Any, Dict, Set

import boto3
import constants
from stravalib import Client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Token:
  token_type: str
  token: str
  expires_at: float
  __table: Any
  __key: str

  @property
  def table_key(self) -> Dict[str, str]:
    return {"token_type": self.__key}

  def __init__(self, table: Any, key: str) -> None:
    self.__key = key
    self.__table = table
    logger.info("Getting record: %s", self.__key)
    try:
      token_resp = self.__table.get_item(Key=self.table_key)["Item"]
    except Exception as e:
      logger.error("Error getting record")
      raise e

    for key in token_resp:
      setattr(self, key, token_resp[key])

  def update(self, token: str, expires_at: float = 0) -> None:
    logger.info("Updating record: %s", self.__key)
    try:
      self.__table.update_item(
        Key=self.table_key,
        UpdateExpression="SET #T = :token, expires_at = :expires_at",
        ExpressionAttributeValues={":token": token, ":expires_at": expires_at},
        ExpressionAttributeNames={"#T": "token"},
      )
    except Exception as e:
      logger.error("Error refreshing token")
      raise e


class StravaClient:
  client: Client

  def __init__(self) -> None:
    self.client = Client()
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(constants.STRAVA_TOKENS_TABLE_NAME)

    access_token = Token(table, constants.ACCESS_TOKEN_KEY)

    if epochtime.time() > access_token.expires_at:
      logger.info("Refreshing token")
      refresh_token = Token(table, constants.REFRESH_TOKEN_KEY)
      try:
        refresh_response = self.client.refresh_access_token(
          constants.STRAVA_CLIENT_ID,
          constants.STRAVA_CLIENT_SECRET,
          refresh_token.token,
        )
      except Exception as e:
        logger.error("Error refreshing token")
        raise e

      refresh_token.update(refresh_response["refresh_token"])
      access_token.update(
        refresh_response["access_token"], refresh_response["expires_at"]
      )
    else:
      self.client.access_token = access_token.token

  def get_activity_external_ids(self) -> Set[str]:
    logger.info("Fetching Strava activities")
    try:
      strava_activities = self.client.get_activities(
        after=datetime.combine(datetime.now(), time.min)
      )
    except Exception as e:
      logger.error("Error fetching Strava activities: %s", e)
      raise e
    return {a.external_id for a in strava_activities if a.external_id}

  def upload_activity(self, fit_data: BufferedReader, external_id: str) -> None:
    logging.info("Uploading activity to Strava: %s", external_id)
    try:
      activity = self.client.upload_activity(
        fit_data,
        data_type="fit",
        external_id=external_id,
      ).wait()
      logging.info("Successfully uploaded activity: %s", activity.id)
    except Exception as e:
      logger.error("Error uploading activity: %s", e)
      raise e
