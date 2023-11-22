import logging
import time as epochtime
from datetime import datetime, time
from io import BufferedReader
from typing import TYPE_CHECKING, Dict, Set

import boto3
from stravalib import Client

from .constants import (
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  STRAVA_CLIENT_ID,
  STRAVA_CLIENT_SECRET,
  STRAVA_TOKENS_TABLE_NAME,
)

if TYPE_CHECKING:
  from mypy_boto3_dynamodb.service_resource import Table

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Token:
  token_type: str
  token: str
  expires_at: float
  __table: Table
  __key: str

  @property
  def table_key(self) -> Dict[str, str]:
    return {"token_type": self.__key}

  def __init__(self, table: Table, key: str) -> None:
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
        ExpressionAttributeValues={":token": token, ":expires_at": int(expires_at)},
        ExpressionAttributeNames={"#T": "token"},
      )
      self.expires_at = expires_at
      self.token = token
    except Exception as e:
      logger.error("Error refreshing token")
      raise e


class StravaClient:
  client: Client

  def __init__(self) -> None:
    self.client = Client()
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(STRAVA_TOKENS_TABLE_NAME)

    access_token = Token(table, ACCESS_TOKEN_KEY)

    if epochtime.time() > access_token.expires_at:
      logger.info("Refreshing token")
      refresh_token = Token(table, REFRESH_TOKEN_KEY)
      try:
        refresh_response = self.client.refresh_access_token(
          STRAVA_CLIENT_ID,
          STRAVA_CLIENT_SECRET,
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
