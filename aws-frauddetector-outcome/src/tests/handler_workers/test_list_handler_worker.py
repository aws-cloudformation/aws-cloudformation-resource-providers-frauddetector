from aws_frauddetector_outcome.helpers import (
    common_helpers,
    client_helpers,
    model_helpers,
)
from aws_frauddetector_outcome import handler_workers
from cloudformation_cli_python_lib import ProgressEvent, OperationStatus, exceptions
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_execute_list_outcome_handler_work_happy_case(monkeypatch):
    # Arrange
    mock_afd_client, model, progress = _setup_execute_list_outcome_handler_work_test(monkeypatch)

    # Act
    handler_workers.execute_list_outcome_handler_work({}, model, progress)

    # Assert
    client_helpers.get_afd_client.assert_called_once()
    assert model_helpers.get_model_for_outcome.call_count == 2
    mock_afd_client.get_outcomes.assert_called_once()


def _setup_execute_list_outcome_handler_work_test(monkeypatch):
    model = unit_test_utils.create_fake_model()
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )

    get_outcomes_response = {'outcomes': [unit_test_utils.FAKE_OUTCOME, unit_test_utils.FAKE_OUTCOME]}
    mock_afd_client = MagicMock()
    mock_afd_client.get_outcomes = MagicMock(return_value=get_outcomes_response)
    mock_get_afd_client = MagicMock(return_value=mock_afd_client)
    mock_get_model_for_outcome = MagicMock(return_value=unit_test_utils.create_fake_model(is_output_model=True))

    monkeypatch.setattr(client_helpers, 'get_afd_client', mock_get_afd_client)
    monkeypatch.setattr(model_helpers, 'get_model_for_outcome', mock_get_model_for_outcome)

    return mock_afd_client, model, progress
