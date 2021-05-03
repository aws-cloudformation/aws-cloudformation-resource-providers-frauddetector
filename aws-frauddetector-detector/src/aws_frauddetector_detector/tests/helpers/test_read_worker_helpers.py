from aws_frauddetector_detector.helpers import (
    read_worker_helpers,
    validation_helpers,
    model_helpers,
)
from cloudformation_cli_python_lib import (
    exceptions,
)
from .. import unit_test_utils
from unittest.mock import MagicMock


def test_validate_detector_exists_and_return_detector_resource_model_success(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    get_detectors_response = {"detectors": [unit_test_utils.FAKE_DETECTOR]}
    mock_check_if_get_detectors_succeeds = MagicMock(return_value=(True, get_detectors_response))
    mock_get_model_for_detector = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_detectors_succeeds",
        mock_check_if_get_detectors_succeeds,
    )
    monkeypatch.setattr(model_helpers, "get_model_for_detector", mock_get_model_for_detector)
    fake_model = unit_test_utils.create_fake_model()

    # Act
    read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(mock_afd_client, fake_model)

    # Assert
    assert mock_check_if_get_detectors_succeeds.call_count == 1
    assert mock_get_model_for_detector.call_count == 1


def test_validate_detector_exists_and_return_detector_resource_model_fail(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_check_if_get_detectors_succeeds = MagicMock(return_value=(False, None))
    mock_get_model_for_detector = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_detectors_succeeds",
        mock_check_if_get_detectors_succeeds,
    )
    monkeypatch.setattr(model_helpers, "get_model_for_detector", mock_get_model_for_detector)
    fake_model = unit_test_utils.create_fake_model()

    # Act
    caught_exception = None
    try:
        read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(mock_afd_client, fake_model)
    except exceptions.NotFound as exception:
        caught_exception = exception

    # Assert
    assert mock_check_if_get_detectors_succeeds.call_count == 1
    assert mock_get_model_for_detector.call_count == 0
    assert caught_exception is not None


def test_validate_detector_exists_and_return_detector_resource_model_empty(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_check_if_get_detectors_succeeds = MagicMock(return_value=(True, {"detectors": []}))
    mock_get_model_for_detector = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_detectors_succeeds",
        mock_check_if_get_detectors_succeeds,
    )
    monkeypatch.setattr(model_helpers, "get_model_for_detector", mock_get_model_for_detector)
    fake_model = unit_test_utils.create_fake_model()

    # Act
    caught_exception = None
    try:
        read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(mock_afd_client, fake_model)
    except exceptions.NotFound as exception:
        caught_exception = exception

    # Assert
    assert mock_check_if_get_detectors_succeeds.call_count == 1
    assert mock_get_model_for_detector.call_count == 0
    assert caught_exception is not None
