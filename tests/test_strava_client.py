import time
from datetime import datetime, timedelta
from unittest.mock import Mock, NonCallableMock

import pytest
from pytest_mock import MockerFixture
from upload_garmin_runs_to_strava.strava_client import StravaClient, Token


class DynamoDBMock(Mock):
  get_item: Mock
  update_item: Mock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.get_item = Mock()
    self.update_item = Mock()


@pytest.fixture
def mock_dynamodb(mocker: MockerFixture) -> DynamoDBMock:
  table_mock = DynamoDBMock()
  table_mock.get_item.return_value = {
    "Item": {
      "token": "123",
      "token_type": "access_token",
      "expires_at": (datetime.now() + timedelta(hours=1)).timestamp(),
    }
  }
  mock = Mock(Table=Mock(return_value=table_mock))
  mocker.patch("boto3.resource", return_value=mock)
  return table_mock


class StravaLibUploadMock(Mock):
  wait: Mock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.wait = Mock()


class StravaLibMock(Mock):
  refresh_access_token: Mock
  get_activities: Mock
  upload_activity: Mock
  upload_activity_wait: StravaLibUploadMock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.refresh_access_token = Mock(
      return_value={
        "access_token": "321",
        "refresh_token": "456",
        "expires_at": (datetime.now() + timedelta(hours=1)).timestamp(),
      },
    )
    self.get_activities = Mock()
    self.upload_activity_wait = StravaLibUploadMock()
    self.upload_activity = Mock(return_value=self.upload_activity_wait)


@pytest.fixture
def mock_stravalib(mocker: MockerFixture) -> StravaLibMock:
  mock = StravaLibMock()
  mocker.patch("upload_garmin_runs_to_strava.strava_client.Client", return_value=mock)
  return mock


class TestToken:
  def test_init(self, mock_dynamodb: DynamoDBMock):
    token = Token(mock_dynamodb, "key")
    assert token.token == "123"
    assert token.expires_at > time.time()
    assert token.token_type == "access_token"

  def test_init_failure(self, mock_dynamodb: DynamoDBMock):
    mock_dynamodb.get_item.side_effect = Exception()
    with pytest.raises(Exception):
      Token(mock_dynamodb, "key")

  def test_update(self, mock_dynamodb: DynamoDBMock):
    token = Token(mock_dynamodb, "key")
    token.update("321", 124)
    assert token.token == "321"
    assert token.expires_at == 124
    assert token.token_type == "access_token"

  def test_update_failure(self, mock_dynamodb: DynamoDBMock):
    mock_dynamodb.update_item.side_effect = Exception()
    token = Token(mock_dynamodb, "key")
    with pytest.raises(Exception):
      token.update("321", 124)


class TestStravaClient:
  def test_init(self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock):
    StravaClient()
    mock_stravalib.assert_not_called()
    assert mock_dynamodb.get_item.call_count == 1

  def test_init_refresh(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    mock_dynamodb.get_item.return_value = {
      "Item": {
        "token": "123",
        "token_type": "access_token",
        "expires_at": 0,
      }
    }
    StravaClient()
    mock_stravalib.refresh_access_token.assert_called_once()
    assert mock_dynamodb.update_item.call_count == 2
    assert mock_dynamodb.get_item.call_count == 2

  def test_init_refresh_error(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    mock_dynamodb.get_item.return_value = {
      "Item": {
        "token": "123",
        "token_type": "access_token",
        "expires_at": 0,
      }
    }
    mock_stravalib.refresh_access_token.side_effect = Exception()
    with pytest.raises(Exception):
      StravaClient()

  def test_get_activities(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    mock_stravalib.get_activities.return_value = [
      NonCallableMock(external_id="1"),
      NonCallableMock(external_id="2"),
    ]
    external_ids = StravaClient().get_activity_external_ids()
    assert len(external_ids) == 2
    assert "1" in external_ids
    assert "2" in external_ids

  def test_get_activities_error(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    mock_stravalib.get_activities.side_effect = Exception()
    with pytest.raises(Exception):
      StravaClient().get_activity_external_ids()

  def test_upload_activity(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    StravaClient().upload_activity(
      NonCallableMock(read=Mock(return_value="data")), "external_id"
    )
    mock_stravalib.upload_activity.assert_called_once()
    mock_stravalib.upload_activity_wait.wait.assert_called_once()

  def test_upload_activity_error(
    self, mock_dynamodb: DynamoDBMock, mock_stravalib: StravaLibMock
  ):
    mock_stravalib.upload_activity_wait.wait.side_effect = Exception()
    with pytest.raises(Exception):
      StravaClient().upload_activity(
        NonCallableMock(read=Mock(return_value="data")), "external_id"
      )
