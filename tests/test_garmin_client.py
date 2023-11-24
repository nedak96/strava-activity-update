from io import StringIO
from unittest.mock import MagicMock, Mock, NonCallableMock, patch

import pytest
from pytest_mock import MockerFixture
from upload_garmin_runs_to_strava.garmin_client import (
  FitData,
  GarminActivity,
  GarminClient,
)


@pytest.fixture
def mock_open(mocker: MockerFixture) -> MagicMock:
  mock = mocker.mock_open(read_data="data")
  mocker.patch("builtins.open", mock)
  return mock


@pytest.fixture
def mock_os_remove(mocker: MockerFixture) -> Mock:
  mock = Mock()
  mocker.patch("os.remove", mock)
  return mock


class MockGarth(Mock):
  load: Mock
  dump: Mock
  login: Mock
  connectapi: Mock
  get: Mock

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.load = Mock()
    self.dump = Mock()
    self.login = Mock()
    self.connectapi = Mock()
    self.get = Mock()


@pytest.fixture
def mock_garth(mocker: MockerFixture) -> MockGarth:
  mock = MockGarth()
  mocker.patch("garth.Client", return_value=mock)
  return mock


class TestGarminActivity:
  def test_init(self):
    activity = GarminActivity({"activityId": "123"})
    assert activity.activity_id == "123"


class TestFitData:
  def test_fit_data(self, mock_open: Mock, mock_os_remove: Mock):
    filename = "file.fit"
    with FitData(filename):
      mock_open.assert_called_once()
      mock_os_remove.assert_not_called()
    mock_os_remove.assert_called_once()


class TestGarminClient:
  def test_init(self, mock_garth: MockGarth):
    GarminClient()
    mock_garth.load.assert_called_once()
    mock_garth.login.assert_not_called()

  def test_init_login(self, mock_garth: MockGarth):
    mock_garth.load.side_effect = Exception()
    GarminClient()
    mock_garth.load.assert_called_once()
    mock_garth.login.assert_called_once()

  def test_get_activities(self, mock_garth: MockGarth):
    mock_garth.connectapi.return_value = [{"activityId": "1"}, {"activityId": "2"}]
    activities = GarminClient().get_activities()
    assert len(activities) == 2
    assert "1" in [a.activity_id for a in activities]
    assert "2" in [a.activity_id for a in activities]

  def test_get_activities_error(self, mock_garth: MockGarth):
    mock_garth.connectapi.side_effect = Exception()
    with pytest.raises(Exception):
      GarminClient().get_activities()

  @patch("upload_garmin_runs_to_strava.garmin_client.ZipFile", return_value=Mock)
  def test_get_fit_data(
    self,
    mock_zipfile: Mock,
    mock_garth: MockGarth,
    mock_open: Mock,
    mock_os_remove: Mock,
  ):
    mock_garth.get.return_value = Mock(
      __enter__=Mock(return_value=NonCallableMock(raw=StringIO("data"))),
      __exit__=Mock(),
    )
    mock_zipfile.return_value = Mock(
      __enter__=Mock(
        return_value=NonCallableMock(
          namelist=Mock(return_value=["123.fit"]),
          extract=Mock(),
        ),
      ),
      __exit__=Mock(),
    )
    fit_data = GarminClient().get_fit_data("123")
    mock_open.assert_called_once_with("./123.zip", "wb")
    mock_os_remove.assert_called_once_with("./123.zip")
    assert fit_data.file_path == "./123.fit"

  def test_get_fit_data_error(self, mock_garth: MockGarth):
    mock_garth.get.side_effect = Exception()
    with pytest.raises(Exception):
      GarminClient().get_fit_data("123")
