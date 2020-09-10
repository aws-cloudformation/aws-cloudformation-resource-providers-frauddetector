from aws_frauddetector_outcome.helpers import common_helpers, client_helpers, validation_helpers
from aws_frauddetector_outcome import handler_workers
from cloudformation_cli_python_lib import ProgressEvent, OperationStatus, exceptions
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_execute_update_outcome_handler_work_happy_case(monkeypatch):
    # Arrange
    model, progress, request = _setup_execute_update_outcome_handler_work_test(monkeypatch)

    # Act
    handler_workers.execute_update_outcome_handler_work({}, model, progress, request)

    # Assert
    client_helpers.get_singleton_afd_client.assert_called_once()
    validation_helpers.check_if_get_outcomes_succeeds.assert_called_once()
    common_helpers.put_outcome_and_return_progress.assert_called_once()
    common_helpers.update_tags.assert_called_once()


def test_execute_update_outcome_handler_work_with_non_existing_outcome_gets_not_found_error(monkeypatch):
    # Arrange
    model, progress, request = _setup_execute_update_outcome_handler_work_test(monkeypatch)
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(False, None))
    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_if_get_outcomes_succeeds)

    # Act/Assert
    _assert_update_handler_results_in_not_found_error({}, model, progress, request)


def test_execute_update_outcome_handler_work_model_has_different_name_gets_not_updatable_error(monkeypatch):
    # Arrange
    model, progress, request = _setup_execute_update_outcome_handler_work_test(monkeypatch)
    model.Name = 'different'

    # Act/Assert
    _assert_update_handler_results_in_not_updatable_error({}, model, progress, request)


def test_execute_update_outcome_handler_work_with_none_tags_removes_tags_attr(monkeypatch):
    # Arrange
    model, progress, request = _setup_execute_update_outcome_handler_work_test(monkeypatch)
    model.Tags = None
    assert 'Tags' in model.__dir__()

    # Act
    handler_workers.execute_update_outcome_handler_work({}, model, progress, request)

    # Assert
    assert 'Tags' not in model.__dir__()


def _setup_execute_update_outcome_handler_work_test(monkeypatch):
    model = unit_test_utils.create_fake_model()
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )

    mock_get_singleton_afd_client = MagicMock(return_value={})
    get_outcomes_response = {'outcomes': [unit_test_utils.FAKE_OUTCOME]}
    mock_check_if_get_outcomes_succeeds = MagicMock(return_value=(True, get_outcomes_response))
    mock_put_outcome_and_return_progress = MagicMock()
    mock_update_tags = MagicMock()

    request = MagicMock()
    request.previousResourceState = unit_test_utils.create_fake_model(is_output_model=True)

    monkeypatch.setattr(client_helpers, 'get_singleton_afd_client', mock_get_singleton_afd_client)
    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_if_get_outcomes_succeeds)
    monkeypatch.setattr(common_helpers, 'put_outcome_and_return_progress', mock_put_outcome_and_return_progress)
    monkeypatch.setattr(common_helpers, 'update_tags', mock_update_tags)

    return model, progress, request


def _assert_update_handler_results_in_not_found_error(afd_client, input_model, progress, request):
    try:
        handler_workers.execute_update_outcome_handler_work(afd_client, input_model, progress, request)
    except exceptions.NotFound:
        assert True
        return
    assert False


def _assert_update_handler_results_in_not_updatable_error(afd_client, input_model, progress, request):
    try:
        handler_workers.execute_update_outcome_handler_work(afd_client, input_model, progress, request)
    except exceptions.NotUpdatable:
        assert True
        return
    assert False
