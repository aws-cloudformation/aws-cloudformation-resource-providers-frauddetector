from aws_frauddetector_outcome.helpers import (
    common_helpers,
    client_helpers,
    validation_helpers,
)
from aws_frauddetector_outcome import handler_workers
from cloudformation_cli_python_lib import ProgressEvent, OperationStatus, exceptions
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_execute_delete_outcome_handler_work_happy_case(monkeypatch):
    # Arrange
    mock_afd_client, model, progress = _setup_execute_delete_outcome_handler_work_test(monkeypatch)

    # Act
    handler_workers.execute_delete_outcome_handler_work({}, model, progress)

    # Assert
    client_helpers.get_afd_client.assert_called_once()
    validation_helpers.check_if_get_outcomes_succeeds.assert_called_once()
    mock_afd_client.delete_outcome.assert_called_once()


def test_execute_delete_outcome_handler_work_outcome_dne_gets_not_found_error(
    monkeypatch,
):
    # Arrange
    mock_afd_client, model, progress = _setup_execute_delete_outcome_handler_work_test(monkeypatch)
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(False, None))
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_outcomes_succeeds",
        mock_check_if_get_outcomes_succeeds,
    )

    # Act/Assert
    _assert_delete_handler_results_in_not_found_error({}, model, progress)


def _setup_execute_delete_outcome_handler_work_test(monkeypatch):
    model = unit_test_utils.create_fake_model()
    progress = ProgressEvent(status=OperationStatus.IN_PROGRESS, resourceModel=model)

    get_outcomes_response = {"outcomes": [unit_test_utils.FAKE_OUTCOME]}
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(True, get_outcomes_response))

    mock_afd_client = MagicMock()
    mock_afd_client.delete_outcome = MagicMock()
    mock_get_afd_client = MagicMock(return_value=mock_afd_client)

    monkeypatch.setattr(client_helpers, "get_afd_client", mock_get_afd_client)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_outcomes_succeeds",
        mock_check_if_get_outcomes_succeeds,
    )

    return mock_afd_client, model, progress


def _assert_delete_handler_results_in_not_found_error(session, input_model, progress):
    try:
        handler_workers.execute_delete_outcome_handler_work(session, input_model, progress)
    except exceptions.NotFound:
        assert True
        return
    assert False
