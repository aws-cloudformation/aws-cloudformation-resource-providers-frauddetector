from aws_frauddetector_outcome.helpers import common_helpers, client_helpers, validation_helpers
from aws_frauddetector_outcome import handler_workers
from cloudformation_cli_python_lib import ProgressEvent, OperationStatus, exceptions
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_execute_create_outcome_handler_work_happy_case(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)

    # Act
    handler_workers.execute_create_outcome_handler_work({}, model, progress)

    # Assert
    client_helpers.get_afd_client.assert_called_once()
    validation_helpers.check_if_get_outcomes_succeeds.assert_called_once()
    common_helpers.put_outcome_and_return_progress.assert_called_once()


def test_execute_create_outcome_handler_work_model_has_arn_gets_invalid_request_error(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)
    model.Arn = 'not-none'

    # Act/Assert
    _assert_create_handler_results_in_invalid_request_error({}, model, progress)


def test_execute_create_outcome_handler_work_model_has_created_time_gets_invalid_request_error(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)
    model.CreatedTime = 'not-none'

    # Act/Assert
    _assert_create_handler_results_in_invalid_request_error({}, model, progress)


def test_execute_create_outcome_handler_work_model_has_updated_time_gets_invalid_request_error(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)
    model.LastUpdatedTime = 'not-none'

    # Act/Assert
    _assert_create_handler_results_in_invalid_request_error({}, model, progress)


def test_execute_create_outcome_handler_work_with_existing_outcome_gets_already_exists_error(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)
    get_outcomes_response = {'outcomes': [unit_test_utils.FAKE_OUTCOME]}
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(True, get_outcomes_response))
    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_if_get_outcomes_succeeds)

    # Act/Assert
    _assert_create_handler_results_in_already_exists_error({}, model, progress)


def test_execute_create_outcome_handler_work_with_none_tags_removes_tags_attr(monkeypatch):
    # Arrange
    model, progress = _setup_execute_create_outcome_handler_work_test(monkeypatch)
    model.Tags = None
    assert 'Tags' in model.__dir__()

    # Act
    handler_workers.execute_create_outcome_handler_work({}, model, progress)

    # Assert
    assert 'Tags' not in model.__dir__()


def _setup_execute_create_outcome_handler_work_test(monkeypatch):
    model = unit_test_utils.create_fake_model()
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )

    mock_get_afd_client = MagicMock(return_value={})
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(False, None))
    mock_put_outcome_and_return_progress = MagicMock()

    monkeypatch.setattr(client_helpers, 'get_afd_client', mock_get_afd_client)
    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_if_get_outcomes_succeeds)
    monkeypatch.setattr(common_helpers, 'put_outcome_and_return_progress', mock_put_outcome_and_return_progress)

    return model, progress


def _assert_create_handler_results_in_already_exists_error(afd_client, input_model, progress):
    try:
        handler_workers.execute_create_outcome_handler_work(afd_client, input_model, progress)
    except exceptions.AlreadyExists:
        assert True
        return
    assert False


def _assert_create_handler_results_in_invalid_request_error(afd_client, input_model, progress):
    try:
        handler_workers.execute_create_outcome_handler_work(afd_client, input_model, progress)
    except exceptions.InvalidRequest:
        assert True
        return
    assert False
