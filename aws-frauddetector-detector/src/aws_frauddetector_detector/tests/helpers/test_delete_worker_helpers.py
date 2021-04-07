from aws_frauddetector_detector.helpers import (
    delete_worker_helpers,
    api_helpers,
)
from .. import unit_test_utils
from unittest.mock import MagicMock


def test_deactivate_and_delete_detector_versions_for_detector_model(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    describe_detector_response = {'detectorVersionSummaries': [
        {'detectorVersionId': '1', 'status': 'DRAFT'},
        {'detectorVersionId': '2', 'status': 'ACTIVE'},
    ]}
    mock_call_describe_detector = MagicMock(return_value=describe_detector_response)
    mock_call_update_detector_version_status = MagicMock()
    mock_call_delete_detector_version = MagicMock()

    monkeypatch.setattr(api_helpers, 'call_describe_detector', mock_call_describe_detector)
    monkeypatch.setattr(api_helpers, 'call_update_detector_version_status', mock_call_update_detector_version_status)
    monkeypatch.setattr(api_helpers, 'call_delete_detector_version', mock_call_delete_detector_version)

    # Act
    delete_worker_helpers.deactivate_and_delete_detector_versions_for_detector_model(mock_afd_client,
                                                                                     fake_model)

    # Assert
    assert mock_call_describe_detector.call_count == 1
    assert mock_call_update_detector_version_status.call_count == 1
    assert mock_call_delete_detector_version.call_count == 2


def test_delete_rules_and_inline_outcomes_for_detector_model(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model(is_output_model=True)
    get_rules_response = {'ruleDetails': [unit_test_utils.FAKE_RULE_DETAIL]}
    mock_call_get_rules = MagicMock(return_value=get_rules_response)
    mock_call_delete_rule = MagicMock()
    mock_call_delete_outcome = MagicMock()

    monkeypatch.setattr(api_helpers, 'call_get_rules', mock_call_get_rules)
    monkeypatch.setattr(api_helpers, 'call_delete_rule', mock_call_delete_rule)
    monkeypatch.setattr(api_helpers, 'call_delete_outcome', mock_call_delete_outcome)

    # Act
    delete_worker_helpers.delete_rules_and_inline_outcomes_for_detector_model(mock_afd_client, fake_model)

    # Assert
    assert mock_call_get_rules.call_count == 1
    assert mock_call_delete_rule.call_count == 1
    assert mock_call_delete_outcome.call_count == 1


def test_delete_detector_for_detector_model(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model(is_output_model=True)
    mock_call_delete_detector = MagicMock()

    monkeypatch.setattr(api_helpers, 'call_delete_detector', mock_call_delete_detector)

    # Act
    delete_worker_helpers.delete_detector_for_detector_model(mock_afd_client, fake_model)

    # Assert
    assert mock_call_delete_detector.call_count == 1


def test_delete_inline_dependencies_for_detector_model(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model(is_output_model=True)
    mock_call_delete_event_type = MagicMock()
    mock_call_delete_variable = MagicMock()
    mock_call_delete_entity_type = MagicMock()
    mock_call_delete_label = MagicMock()

    monkeypatch.setattr(api_helpers, 'call_delete_event_type', mock_call_delete_event_type)
    monkeypatch.setattr(api_helpers, 'call_delete_variable', mock_call_delete_variable)
    monkeypatch.setattr(api_helpers, 'call_delete_entity_type', mock_call_delete_entity_type)
    monkeypatch.setattr(api_helpers, 'call_delete_label', mock_call_delete_label)

    # Act
    delete_worker_helpers.delete_inline_dependencies_for_detector_model(mock_afd_client, fake_model)

    # Assert
    assert mock_call_delete_event_type.call_count == 1
    assert mock_call_delete_variable.call_count == 2
    assert mock_call_delete_entity_type.call_count == 1
    assert mock_call_delete_label.call_count == 2
