from unittest.mock import Mock, NonCallableMock

import pytest
from pytest_mock import MockerFixture
from upload_garmin_runs_to_strava import handler
from upload_garmin_runs_to_strava.garmin_client import GarminActivity


class MockGarminClient(NonCallableMock):
  get_activities: Mock
  get_fit_data: Mock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.get_activities = Mock()
    self.get_fit_data = Mock()


@pytest.fixture
def mock_garmin_client(mocker: MockerFixture) -> MockGarminClient:
  mock = MockGarminClient()
  mock.get_activities.return_value = [
    GarminActivity({"activityId": "1"}),
    GarminActivity({"activityId": "2"}),
  ]
  mock.get_fit_data.return_value = Mock(
    __enter__=Mock(return_value="data"),
    __exit__=Mock(),
  )
  mocker.patch("upload_garmin_runs_to_strava.index.GarminClient", return_value=mock)
  return mock


class MockStravaClient(NonCallableMock):
  get_activity_external_ids: Mock
  upload_activity: Mock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.get_activity_external_ids = Mock()
    self.upload_activity = Mock()


@pytest.fixture
def mock_strava_client(mocker: MockerFixture) -> MockStravaClient:
  mock = MockStravaClient()
  mock.get_activity_external_ids.return_value = {"2.fit"}
  mocker.patch("upload_garmin_runs_to_strava.index.StravaClient", return_value=mock)
  return mock


class TestHandler:
  def test_handler(
    self, mock_garmin_client: MockGarminClient, mock_strava_client: MockStravaClient
  ):
    handler(NonCallableMock(), NonCallableMock())
    mock_garmin_client.get_activities.assert_called_once()
    mock_strava_client.get_activity_external_ids.assert_called_once()
    mock_garmin_client.get_fit_data.assert_called_once_with("1")
    mock_strava_client.upload_activity.assert_called_once_with("data", "1")

  def test_handler_exit_early(
    self, mock_garmin_client: MockGarminClient, mock_strava_client: MockStravaClient
  ):
    mock_garmin_client.get_activities.return_value = []
    handler(NonCallableMock(), NonCallableMock())
    mock_garmin_client.get_activities.assert_called_once()
    mock_strava_client.get_activity_external_ids.assert_not_called()
