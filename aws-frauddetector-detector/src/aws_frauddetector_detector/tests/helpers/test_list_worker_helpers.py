from aws_frauddetector_detector.helpers import (
    list_worker_helpers,
    api_helpers,
    model_helpers,
)
from .. import unit_test_utils
from unittest.mock import MagicMock


def test_list_detector_models(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    get_detectors_response = {'detectors': [unit_test_utils.FAKE_DETECTOR, unit_test_utils.FAKE_DETECTOR]}
    mock_call_get_detectors = MagicMock(return_value=get_detectors_response)
    mock_get_model_for_detector = MagicMock()
    monkeypatch.setattr(api_helpers, 'call_get_detectors', mock_call_get_detectors)
    monkeypatch.setattr(model_helpers, 'get_model_for_detector', mock_get_model_for_detector)

    # Act
    models = list_worker_helpers.list_detector_models(mock_afd_client)

    # Assert
    assert len(models) == 2
    assert mock_call_get_detectors.call_count == 1
    assert mock_get_model_for_detector.call_count == 2
