from aws_frauddetector_detector.helpers import model_helpers
from aws_frauddetector_detector import models
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_put_detector_for_model():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.put_detector = MagicMock()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.EventType.Name = None

    # Act
    model_helpers.put_detector_for_model(mock_afd_client, fake_model)

    # Assert
    assert mock_afd_client.put_detector.call_count == 1


def test_create_rule_for_rule_model():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    # create rule actually only returns a rule with rule id, rule version, and detector id, but this works as a test
    create_rule_response = {"rule": unit_test_utils.FAKE_RULE_DETAIL}
    mock_afd_client.create_rule = MagicMock(return_value=create_rule_response)
    fake_detector_model = unit_test_utils.create_fake_model()
    fake_rule_model = unit_test_utils.create_fake_rule()

    # Act
    result = model_helpers.create_rule_for_rule_model(mock_afd_client, fake_rule_model, fake_detector_model)

    # Assert
    assert mock_afd_client.create_rule.call_count == 1
    assert result == unit_test_utils.FAKE_RULE_DETAIL


def test_get_model_for_detector():
    # Arrange
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    get_variables_response_1 = {"variables": [unit_test_utils.FAKE_IP_VARIABLE]}
    get_variables_response_2 = {"variables": [unit_test_utils.FAKE_EMAIL_VARIABLE]}
    get_labels_response_1 = {"labels": [unit_test_utils.FAKE_FRAUD_LABEL]}
    get_labels_response_2 = {"labels": [unit_test_utils.FAKE_LEGIT_LABEL]}
    get_entity_types_response = {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]}
    describe_detector_response = {
        "detectorVersionSummaries": [
            {"detectorVersionId": "1"},
            {"detectorVersionId": "2"},
        ]
    }
    get_detector_version_response = unit_test_utils.FAKE_DETECTOR_VERSION_WITH_EXTERNAL_MODEL_AND_MODEL_VERSION
    get_rules_response = {"ruleDetails": [unit_test_utils.FAKE_RULE_DETAIL]}
    get_outcomes_response = {"outcomes": [unit_test_utils.FAKE_OUTCOME]}
    get_external_models_response = {"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)
    mock_afd_client.get_variables = MagicMock()
    mock_afd_client.get_variables.side_effect = [
        get_variables_response_1,
        get_variables_response_2,
    ]
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.get_labels.side_effect = [
        get_labels_response_1,
        get_labels_response_2,
    ]
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)
    mock_afd_client.describe_detector = MagicMock(return_value=describe_detector_response)
    mock_afd_client.get_detector_version = MagicMock(return_value=get_detector_version_response)
    mock_afd_client.get_rules = MagicMock(return_value=get_rules_response)
    mock_afd_client.get_outcomes = MagicMock(return_value=get_outcomes_response)
    mock_afd_client.get_external_models = MagicMock(return_value=get_external_models_response)
    mock_afd_client.get_external_models = MagicMock(return_value=get_external_models_response)

    fake_detector = unit_test_utils.FAKE_DETECTOR
    fake_model = unit_test_utils.create_fake_model()

    associated_models = [
        models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL_ARN),
        models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN),
    ]
    fake_model.AssociatedModels = associated_models

    output_model = unit_test_utils.create_fake_model(is_output_model=True)
    output_model.AssociatedModels = associated_models

    # Act
    model_result = model_helpers.get_model_for_detector(mock_afd_client, fake_detector, fake_model)

    # Assert
    assert mock_afd_client.list_tags_for_resource.call_count == 9
    assert mock_afd_client.get_event_types.call_count == 1
    assert mock_afd_client.get_variables.call_count == 2
    assert mock_afd_client.get_labels.call_count == 2
    assert mock_afd_client.get_entity_types.call_count == 1
    assert mock_afd_client.describe_detector.call_count == 1
    assert mock_afd_client.get_detector_version.call_count == 1
    assert mock_afd_client.get_rules.call_count == 1
    assert mock_afd_client.get_outcomes.call_count == 1
    assert mock_afd_client.get_external_models.call_count == 1
    assert model_result == output_model


def test_get_model_for_detector_with_references():
    # Arrange
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    describe_detector_response = {
        "detectorVersionSummaries": [
            {"detectorVersionId": "1"},
            {"detectorVersionId": "2"},
        ]
    }
    get_detector_version_response = unit_test_utils.FAKE_DETECTOR_VERSION
    get_rules_response = {"ruleDetails": [unit_test_utils.FAKE_RULE_DETAIL]}
    get_outcomes_response = {"outcomes": [unit_test_utils.FAKE_OUTCOME]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)
    mock_afd_client.describe_detector = MagicMock(return_value=describe_detector_response)
    mock_afd_client.get_detector_version = MagicMock(return_value=get_detector_version_response)
    mock_afd_client.get_rules = MagicMock(return_value=get_rules_response)
    mock_afd_client.get_outcomes = MagicMock(return_value=get_outcomes_response)

    fake_detector = unit_test_utils.FAKE_DETECTOR
    fake_model = unit_test_utils.create_fake_model_with_references()
    expected_output_model = unit_test_utils.create_fake_model_with_references(is_output_model=True)

    # Act
    model_result = model_helpers.get_model_for_detector(mock_afd_client, fake_detector, fake_model)

    # Assert
    assert mock_afd_client.list_tags_for_resource.call_count == 2
    assert mock_afd_client.get_event_types.call_count == 1
    assert mock_afd_client.get_variables.call_count == 0
    assert mock_afd_client.get_labels.call_count == 0
    assert mock_afd_client.get_entity_types.call_count == 0
    assert mock_afd_client.describe_detector.call_count == 1
    assert mock_afd_client.get_detector_version.call_count == 1
    assert mock_afd_client.get_rules.call_count == 1
    assert mock_afd_client.get_outcomes.call_count == 1
    _assert_referenced_input_model_output_model_equality(model_result, expected_output_model)


def test_get_event_type_and_return_event_type_model():
    # Arrange
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    get_variables_response_1 = {"variables": [unit_test_utils.FAKE_IP_VARIABLE]}
    get_variables_response_2 = {"variables": [unit_test_utils.FAKE_EMAIL_VARIABLE]}
    get_labels_response_1 = {"labels": [unit_test_utils.FAKE_FRAUD_LABEL]}
    get_labels_response_2 = {"labels": [unit_test_utils.FAKE_LEGIT_LABEL]}
    get_entity_types_response = {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)
    mock_afd_client.get_variables = MagicMock()
    mock_afd_client.get_variables.side_effect = [
        get_variables_response_1,
        get_variables_response_2,
    ]
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.get_labels.side_effect = [
        get_labels_response_1,
        get_labels_response_2,
    ]
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)

    # Act
    model_result = model_helpers.get_event_type_and_return_event_type_model(
        mock_afd_client, unit_test_utils.create_fake_event_type()
    )

    # Assert
    assert mock_afd_client.list_tags_for_resource.call_count == 6
    assert mock_afd_client.get_event_types.call_count == 1
    assert mock_afd_client.get_variables.call_count == 2
    assert mock_afd_client.get_labels.call_count == 2
    assert mock_afd_client.get_entity_types.call_count == 1
    assert model_result == unit_test_utils.create_fake_event_type(is_output_model=True)


def test_get_inline_resources_for_event_type():
    # Arrange - fake model has all inline dependencies
    fake_model = unit_test_utils.create_fake_event_type()

    # Act
    inline_resources: dict = model_helpers.get_inline_resources_for_event_type(fake_model)

    # Assert
    assert len(inline_resources) == 3
    assert len(inline_resources["event_variables"]) == len(fake_model.EventVariables)
    assert len(inline_resources["labels"]) == len(fake_model.Labels)
    assert len(inline_resources["entity_types"]) == len(fake_model.EntityTypes)


def _assert_referenced_input_model_output_model_equality(
    actual_model: models.ResourceModel, expected_model: models.ResourceModel
):
    """
    We trim some attributes for referenced entities, so the cfn generated models.py will complain on repr()
    (Opportunity for cfn python plugin to improve by being more robust on repr() and __str__())
    To work around, tread lightly on Rules and EventType, which have referenced resources
    """
    assert actual_model.DetectorId == expected_model.DetectorId
    assert actual_model.DetectorVersionStatus == expected_model.DetectorVersionStatus
    assert actual_model.DetectorVersionId == expected_model.DetectorVersionId
    assert actual_model.RuleExecutionMode == expected_model.RuleExecutionMode
    assert actual_model.Tags == expected_model.Tags
    assert actual_model.Description == expected_model.Description
    assert actual_model.Arn == expected_model.Arn
    assert actual_model.CreatedTime == expected_model.CreatedTime
    assert actual_model.LastUpdatedTime == expected_model.LastUpdatedTime

    # event type
    assert actual_model.EventType.Arn == expected_model.EventType.Arn
    assert actual_model.EventType.Inline == expected_model.EventType.Inline

    # rules
    number_of_rules = len(actual_model.Rules)
    for i in range(number_of_rules):
        actual_rule_model = actual_model.Rules[i]
        expected_rule_model = expected_model.Rules[i]
        assert actual_rule_model.RuleId == expected_rule_model.RuleId
        assert actual_rule_model.RuleVersion == expected_rule_model.RuleVersion
        assert actual_rule_model.DetectorId == expected_rule_model.DetectorId
        assert actual_rule_model.Expression == expected_rule_model.Expression
        assert actual_rule_model.Language == expected_rule_model.Language
        assert actual_rule_model.Arn == expected_rule_model.Arn
        assert actual_rule_model.Description == expected_rule_model.Description
        assert actual_rule_model.Tags == expected_rule_model.Tags
        assert actual_rule_model.CreatedTime == expected_rule_model.CreatedTime
        assert actual_rule_model.LastUpdatedTime == expected_rule_model.LastUpdatedTime

        # outcomes
        number_of_outcomes = len(actual_rule_model.Outcomes)
        for j in range(number_of_outcomes):
            actual_outcome = actual_rule_model.Outcomes[j]
            expected_outcome = expected_rule_model.Outcomes[j]
            assert actual_outcome.Arn == expected_outcome.Arn
            assert actual_outcome.Inline == expected_outcome.Inline
