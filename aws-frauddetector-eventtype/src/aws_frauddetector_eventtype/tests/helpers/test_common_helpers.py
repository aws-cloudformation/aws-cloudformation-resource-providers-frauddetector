from ...helpers import (
    common_helpers,
    model_helpers,  # for monkeypatch
    validation_helpers,  # for monkeypatch
)

from cloudformation_cli_python_lib import (
    ProgressEvent,
    OperationStatus,
)
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_update_tags():
    # Arrange
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}
    fake_tag_keys = [tag.get("key", "") for tag in unit_test_utils.FAKE_TAGS]

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.tag_resource = MagicMock()
    mock_afd_client.untag_resource = MagicMock()

    # Act
    common_helpers.update_tags(
        mock_afd_client,
        unit_test_utils.FAKE_ARN,
        unit_test_utils.FAKE_TAG_MODELS_DIFFERENT,
    )

    # Assert
    mock_afd_client.untag_resource.assert_called_once_with(resourceARN=unit_test_utils.FAKE_ARN, tagKeys=fake_tag_keys)
    mock_afd_client.tag_resource.assert_called_once_with(
        resourceARN=unit_test_utils.FAKE_ARN, tags=unit_test_utils.FAKE_TAGS_DIFFERENT
    )


def test_put_event_type_and_return_progress(monkeypatch):
    # Arrange
    mock_afd_client, input_model, output_model = _setup_put_event_type_test()
    fake_output_model = unit_test_utils.create_fake_model(True)
    fake_output_model = _add_extra_attributes_for_event_type(fake_output_model)
    mock_get_event_type_and_return_model = MagicMock(return_value=fake_output_model)

    monkeypatch.setattr(
        model_helpers,
        "get_event_type_and_return_model",
        mock_get_event_type_and_return_model,
    )

    # Act/Assert
    _act_and_assert_put_event_type_for_given_model(mock_afd_client, input_model, output_model)


def test_create_inline_event_variable():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.create_variable = MagicMock()
    fake_input_model = unit_test_utils.create_fake_model()
    fake_event_variable = fake_input_model.EventVariables[0]
    fake_tags = model_helpers.get_tags_from_tag_models(fake_event_variable.Tags)

    # Act
    common_helpers.create_inline_event_variable(mock_afd_client, fake_event_variable)

    # Assert
    mock_afd_client.create_variable.assert_called_once_with(
        name=fake_event_variable.Name,
        dataSource=fake_event_variable.DataSource,
        dataType=fake_event_variable.DataType,
        defaultValue=fake_event_variable.DefaultValue,
        description=fake_event_variable.Description,
        variableType=fake_event_variable.VariableType,
        tags=fake_tags,
    )


def test_create_inline_event_variables():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.batch_create_variable = MagicMock()
    fake_input_model = unit_test_utils.create_fake_model()
    fake_event_variables = fake_input_model.EventVariables
    # Calling internal (would-be-package-private) method to re-build expected arguments
    tags, variable_entries = common_helpers._get_tags_and_variable_entries_from_inline_event_variables(
        fake_event_variables
    )

    # Act
    common_helpers.create_inline_event_variables(mock_afd_client, fake_event_variables)

    # Assert
    mock_afd_client.batch_create_variable.assert_called_once_with(
        tags=tags,
        variableEntries=variable_entries,
    )


def test_put_inline_label():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.put_label = MagicMock()
    fake_input_model = unit_test_utils.create_fake_model()
    fake_label = fake_input_model.Labels[0]
    fake_tags = model_helpers.get_tags_from_tag_models(fake_label.Tags)

    # Act
    common_helpers.put_inline_label(mock_afd_client, fake_label)

    # Assert
    mock_afd_client.put_label.assert_called_once_with(
        name=fake_label.Name, description=fake_label.Description, tags=fake_tags
    )


def test_put_inline_entity_type():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.put_entity_type = MagicMock()
    fake_input_model = unit_test_utils.create_fake_model()
    fake_entity_type = fake_input_model.EntityTypes[0]
    fake_tags = model_helpers.get_tags_from_tag_models(fake_entity_type.Tags)

    # Act
    common_helpers.put_inline_entity_type(mock_afd_client, fake_entity_type)

    # Assert
    mock_afd_client.put_entity_type.assert_called_once_with(
        name=fake_entity_type.Name,
        description=fake_entity_type.Description,
        tags=fake_tags,
    )


def _setup_update_event_variables_test(monkeypatch):
    mock_afd_client = MagicMock()
    input_model = unit_test_utils.create_fake_model()
    input_model = _add_extra_attributes_for_event_type(input_model)
    existing_variable_model = unit_test_utils.create_fake_model()
    existing_variable_model = _add_extra_attributes_for_variable(existing_variable_model)
    existing_variables = [existing_variable_model]
    variable_entry_argument = unit_test_utils.create_fake_variable()
    del variable_entry_argument["createdTime"]
    del variable_entry_argument["lastUpdatedTime"]
    del variable_entry_argument["arn"]
    missing_names = [unit_test_utils.FAKE_NAME]
    mock_check_which_variables_exist = MagicMock(return_value=(existing_variables, missing_names))
    mock_check_variable_differences = MagicMock(
        return_value={"defaultValue": True, "description": False, "variableType": False}
    )
    mock_get_variable_entry_argument_from_event_variable_model = MagicMock(return_value=variable_entry_argument)

    monkeypatch.setattr(
        validation_helpers,
        "check_which_variables_exist",
        mock_check_which_variables_exist,
    )
    monkeypatch.setattr(
        validation_helpers,
        "check_variable_differences",
        mock_check_variable_differences,
    )
    monkeypatch.setattr(
        model_helpers,
        "get_variable_entry_argument_from_event_variable_model",
        mock_get_variable_entry_argument_from_event_variable_model,
    )

    return mock_afd_client, input_model


def _setup_put_event_type_test():
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.put_event_type = MagicMock()
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)

    model = unit_test_utils.create_fake_model()
    model = _add_extra_attributes_for_event_type(model)
    expected_model = unit_test_utils.create_fake_model(is_output_model=True)
    return mock_afd_client, model, expected_model


def _add_extra_attributes_for_event_type(model):
    fake_input_model = unit_test_utils.create_fake_model()
    model.Labels = fake_input_model.Labels
    model.EventVariables = fake_input_model.EventVariables
    model.EntityTypes = fake_input_model.EntityTypes
    model.EventTypeName = unit_test_utils.FAKE_NAME
    return model


def _add_extra_attributes_for_variable(model):
    model.dataSource = unit_test_utils.EVENT
    model.dataType = unit_test_utils.STRING
    model.defaultValue = unit_test_utils.DEFAULT
    model.variableType = unit_test_utils.EMAIL_ADDRESS
    return model


def _act_and_assert_put_event_type_for_given_model(afd_client, input_model, output_model):
    initial_progress = ProgressEvent(status=OperationStatus.IN_PROGRESS)
    result_progress = common_helpers.put_event_type_and_return_progress(afd_client, input_model, initial_progress)
    result_model = result_progress.resourceModel
    # Need to assert each sub-attribute, otherwise full equivalence will check readonly properties too (e.g. Arn)
    assert result_model.Name == output_model.Name
    assert result_model.Tags == output_model.Tags
    assert result_model.Description == output_model.Description
    for i in range(0, len(result_model.EventVariables)):
        actual_event_variable = result_model.EventVariables[i]
        expected_event_variable = output_model.EventVariables[i]
        assert actual_event_variable.Name == expected_event_variable.Name
        assert actual_event_variable.DataSource == expected_event_variable.DataSource
        assert actual_event_variable.DataType == expected_event_variable.DataType
        assert actual_event_variable.DefaultValue == expected_event_variable.DefaultValue
        assert actual_event_variable.VariableType == expected_event_variable.VariableType
        assert actual_event_variable.Description == expected_event_variable.Description
        assert actual_event_variable.Tags == expected_event_variable.Tags
    for i in range(0, len(result_model.EntityTypes)):
        actual_entity_type = result_model.EntityTypes[i]
        expected_entity_type = output_model.EntityTypes[i]
        assert actual_entity_type.Name == expected_entity_type.Name
        assert actual_entity_type.Description == expected_entity_type.Description
        assert actual_entity_type.Tags == expected_entity_type.Tags
    for i in range(0, len(result_model.Labels)):
        actual_label = result_model.Labels[i]
        expected_label = output_model.Labels[i]
        assert actual_label.Name == expected_label.Name
        assert actual_label.Description == expected_label.Description
        assert actual_label.Tags == expected_label.Tags
