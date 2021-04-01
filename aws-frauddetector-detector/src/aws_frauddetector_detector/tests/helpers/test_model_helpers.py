from aws_frauddetector_detector.helpers import model_helpers
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_get_event_type_and_return_event_type_model():
    # Arrange
    list_tags_response = {'tags': unit_test_utils.FAKE_TAGS}
    get_event_types_response = {'eventTypes': [unit_test_utils.FAKE_EVENT_TYPE]}
    get_variables_response_1 = {'variables': [unit_test_utils.FAKE_IP_VARIABLE]}
    get_variables_response_2 = {'variables': [unit_test_utils.FAKE_EMAIL_VARIABLE]}
    get_labels_response_1 = {'labels': [unit_test_utils.FAKE_FRAUD_LABEL]}
    get_labels_response_2 = {'labels': [unit_test_utils.FAKE_LEGIT_LABEL]}
    get_entity_types_response = {'entityTypes': [unit_test_utils.FAKE_ENTITY_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)
    mock_afd_client.get_variables = MagicMock()
    mock_afd_client.get_variables.side_effect = [get_variables_response_1, get_variables_response_2]
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.get_labels.side_effect = [get_labels_response_1, get_labels_response_2]
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)

    # Act
    model_result = model_helpers.get_event_type_and_return_event_type_model(mock_afd_client,
                                                                            unit_test_utils.create_fake_event_type())

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
    assert len(inline_resources['event_variables']) == len(fake_model.EventVariables)
    assert len(inline_resources['labels']) == len(fake_model.Labels)
    assert len(inline_resources['entity_types']) == len(fake_model.EntityTypes)
