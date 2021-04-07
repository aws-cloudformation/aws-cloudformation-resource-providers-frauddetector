from aws_frauddetector_detector.helpers import (
    create_worker_helpers,
    validation_helpers,
)
from .. import unit_test_utils
from unittest.mock import MagicMock


def test_validate_dependencies_for_detector_create(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))

    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_get_outcomes)
    monkeypatch.setattr(validation_helpers, 'check_if_get_event_types_succeeds', mock_check_get_event_types)
    monkeypatch.setattr(validation_helpers, 'check_if_get_variables_succeeds', mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, 'check_if_get_labels_succeeds', mock_check_get_labels)
    monkeypatch.setattr(validation_helpers, 'check_if_get_entity_types_succeeds', mock_check_get_entity_types)

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1


def test_validate_dependencies_for_detector_create_with_referenced_dependencies(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model_with_references()
    get_outcomes_response = {'outcomes': [unit_test_utils.FAKE_OUTCOME]}
    mock_check_get_outcomes = MagicMock(return_value=(True, get_outcomes_response))
    get_event_types_response = {'eventTypes': [unit_test_utils.FAKE_EVENT_TYPE]}
    mock_check_get_event_types = MagicMock(return_value=(True, get_event_types_response))

    mock_check_get_variables = MagicMock()
    mock_check_get_labels = MagicMock()
    mock_check_get_entity_types = MagicMock()

    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_get_outcomes)
    monkeypatch.setattr(validation_helpers, 'check_if_get_event_types_succeeds', mock_check_get_event_types)
    monkeypatch.setattr(validation_helpers, 'check_if_get_variables_succeeds', mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, 'check_if_get_labels_succeeds', mock_check_get_labels)
    monkeypatch.setattr(validation_helpers, 'check_if_get_entity_types_succeeds', mock_check_get_entity_types)

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 1
    assert mock_check_get_event_types.call_count == 1
    assert mock_check_get_variables.call_count == 0
    assert mock_check_get_labels.call_count == 0
    assert mock_check_get_entity_types.call_count == 0


def test_validate_dependencies_for_detector_create_with_inline_event_type_with_referenced_dependencies(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.EventType = unit_test_utils.create_fake_inline_event_type_with_referenced_dependencies()
    get_outcomes_response = {'outcomes': [unit_test_utils.FAKE_OUTCOME]}
    mock_check_get_outcomes = MagicMock(return_value=(True, get_outcomes_response))
    get_event_types_response = {'eventTypes': [unit_test_utils.FAKE_EVENT_TYPE]}
    mock_check_get_event_types = MagicMock(return_value=(True, get_event_types_response))
    get_variables_response = {'variables': [unit_test_utils.FAKE_IP_VARIABLE, unit_test_utils.FAKE_EMAIL_VARIABLE]}
    mock_check_get_variables = MagicMock(return_value=(True, get_variables_response))
    get_labels_response = {'labels': [unit_test_utils.FAKE_FRAUD_LABEL, unit_test_utils.FAKE_LEGIT_LABEL]}
    mock_check_get_labels = MagicMock(return_value=(True, get_labels_response))
    get_entity_types_response = {'entityTypes': [unit_test_utils.FAKE_ENTITY_TYPE]}
    mock_check_get_entity_types = MagicMock(return_value=(True, get_entity_types_response))

    monkeypatch.setattr(validation_helpers, 'check_if_get_outcomes_succeeds', mock_check_get_outcomes)
    monkeypatch.setattr(validation_helpers, 'check_if_get_event_types_succeeds', mock_check_get_event_types)
    monkeypatch.setattr(validation_helpers, 'check_if_get_variables_succeeds', mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, 'check_if_get_labels_succeeds', mock_check_get_labels)
    monkeypatch.setattr(validation_helpers, 'check_if_get_entity_types_succeeds', mock_check_get_entity_types)

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
