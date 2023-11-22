import os

IS_LOCAL = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is None
DOWNLOAD_DIR = "." if IS_LOCAL else "/tmp"

STRAVA_TOKENS_TABLE_NAME = os.environ["STRAVA_TOKENS_TABLE_NAME"]
ACCESS_TOKEN_KEY = os.environ["ACCESS_TOKEN_KEY"]
REFRESH_TOKEN_KEY = os.environ["REFRESH_TOKEN_KEY"]

STRAVA_CLIENT_ID = int(os.environ["STRAVA_CLIENT_ID"])
STRAVA_CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

GARMIN_USERNAME = os.environ["GARMIN_USERNAME"]
GARMIN_PASSWORD = os.environ["GARMIN_PASSWORD"]
GARMIN_ACTIVITIES_PATH = "/activitylist-service/activities/search/activities"
GARMIN_DOWNLOAD_FILES_PATH = "/download-service/files/activity"
GARMIN_TOKEN_FILE_PATH = f"{DOWNLOAD_DIR}/.garminconnect"
