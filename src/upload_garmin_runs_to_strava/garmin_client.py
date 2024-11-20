import logging
import os
import shutil
from datetime import datetime
from enum import Enum
from io import BufferedReader
from typing import Any, Dict, List
from zipfile import ZipFile
from zoneinfo import ZoneInfo

import garth

from .constants import (
  DOWNLOAD_DIR,
  GARMIN_ACTIVITIES_PATH,
  GARMIN_DOWNLOAD_FILES_PATH,
  GARMIN_PASSWORD,
  GARMIN_TOKEN_FILE_PATH,
  GARMIN_USERNAME,
)

tz = ZoneInfo("America/New_York")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ActivityType(Enum):
  RUNNING = "running"
  HIKING = "hiking"
  CYCLING = "cycling"
  SWIMMING = "swimming"


class GarminActivity:
  activity_id: str

  def __init__(self, activity: Dict[str, Any]) -> None:
    self.activity_id = activity["activityId"]


class FitData:
  file_path: str
  file: BufferedReader

  def __init__(self, file_path) -> None:
    self.file_path = file_path

  def __enter__(self) -> BufferedReader:
    self.file = open(self.file_path, "rb")
    return self.file

  def __exit__(self, type, value, traceback) -> None:
    self.file.__exit__(type, value, traceback)
    os.remove(self.file_path)


class GarminClient:
  garth_client: garth.Client

  def __init__(self) -> None:
    self.garth_client = garth.Client()
    try:
      logger.info("Logging in with tokenfile")
      self.garth_client.load(GARMIN_TOKEN_FILE_PATH)
    except Exception as e:
      logger.warning(
        "Error logging in with tokenfile, logging in with credentials: %s",
        e,
      )
      self.garth_client.login(GARMIN_USERNAME, GARMIN_PASSWORD)
      self.garth_client.dump(GARMIN_TOKEN_FILE_PATH)

  def get_activities(self, activity_type: ActivityType) -> List[GarminActivity]:
    logger.info("Fetching activities from Garmin for type: %s", activity_type.value)
    try:
      activities = self.garth_client.connectapi(
        GARMIN_ACTIVITIES_PATH,
        params={
          "startDate": datetime.now(tz).strftime("%Y-%m-%d"),
          "activityType": activity_type.value,
        },
      )
    except Exception as e:
      logger.error("Error fetching activities from Garmin: %s", e)
      raise e

    return [GarminActivity(a) for a in activities]

  def get_fit_data(self, activityId) -> FitData:
    zip_file_path = f"{DOWNLOAD_DIR}/{activityId}.zip"
    fit_file_path: str
    logger.info("Downloading activity from Garmin: %s", activityId)
    try:
      with self.garth_client.get(
        "connectapi",
        f"{GARMIN_DOWNLOAD_FILES_PATH}/{activityId}",
        api=True,
        stream=True,
      ) as resp:
        logger.info("Save data to zip file: %s", activityId)
        with open(zip_file_path, "wb") as f:
          shutil.copyfileobj(resp.raw, f)
    except Exception as e:
      logger.error("Error fetching Garmin activity: %s", e)
      raise e

    logger.info("Extract zip data: %s", activityId)
    with ZipFile(zip_file_path) as zip:
      filename = zip.namelist()[0]
      fit_file_path = f"{DOWNLOAD_DIR}/{filename}"
      zip.extract(filename, path=DOWNLOAD_DIR)
    os.remove(zip_file_path)

    return FitData(fit_file_path)
