from ...helpers import validation_helpers, util
from ...models import EventVariable
from botocore.exceptions import ClientError
from unittest.mock import MagicMock
from .. import unit_test_utils
from cloudformation_cli_python_lib import (
    exceptions,
)


FAKE_VALID_ARN = "arn:aws:frauddetector:us-east-1:123456789012:variable/fake"


def test_check_if_get_labels_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_labels.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_labels"),
        ClientError({"Code": "", "Message": ""}, "get_labels"),
    ]

    # Act
    result = validation_helpers.check_if_get_labels_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_labels_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_labels_response = {"labels": [unit_test_utils.FAKE_FRAUD_LABEL]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock(return_value=get_labels_response)

    # Act
    result = validation_helpers.check_if_get_labels_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_labels_response


def test_check_if_get_entity_types_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_entity_types.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
    ]

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_entity_types_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_entity_types_response = {"entity_types": [unit_test_utils.FAKE_ENTITY_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_entity_types_response


def test_check_if_get_variables_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_variables = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_variables.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_variables"),
        ClientError({"Code": "", "Message": ""}, "get_variables"),
    ]

    # Act
    result = validation_helpers.check_if_get_variables_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_variables_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_variables_response = {"variables": [unit_test_utils.FAKE_IP_VARIABLE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_variables = MagicMock(return_value=get_variables_response)

    # Act
    result = validation_helpers.check_if_get_variables_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_variables_response


def test_check_if_get_event_types_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_event_types = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_event_types.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_event_types"),
        ClientError({"Code": "", "Message": ""}, "get_event_types"),
    ]

    # Act
    result = validation_helpers.check_if_get_event_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_event_types_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_event_types_response = {"event_types": [unit_test_utils.FAKE_EVENT_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)

    # Act
    result = validation_helpers.check_if_get_event_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_event_types_response


def test_check_batch_get_variable_errors_happy_case():
    # Arrange
    batch_get_variable_response = {"errors": [], "variables": []}
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.batch_get_variable = MagicMock(return_value=batch_get_variable_response)

    # Act
    result = validation_helpers.check_batch_get_variable_errors(mock_afd_client, [])

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] == batch_get_variable_response


def test_check_batch_get_variable_errors_client_error_case():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.batch_get_variable.side_effect = [
        ClientError({"Code": "", "Message": ""}, "batch_get_variable"),
        ClientError({"Code": "", "Message": ""}, "batch_get_variable"),
    ]

    # Act
    result = validation_helpers.check_batch_get_variable_errors(mock_afd_client, ["name1", "name2"])

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] == {}


def test_check_variable_entries_are_valid_missing_attributes():
    # Arrange
    variable_entries = [{"missing": "attributes"}]
    args = {"variableEntries": variable_entries}

    # Act
    exception_thrown = None
    try:
        validation_helpers.check_variable_entries_are_valid(args)
    except exceptions.InvalidRequest as invalid_request_exception:
        exception_thrown = invalid_request_exception

    # Assert
    assert exception_thrown is not None
    assert "did not have the following required attributes" in f"{exception_thrown}"


def test_check_variable_entries_are_valid_extra_attributes():
    # Arrange
    variable_entries = [
        {"dataSource": "valid", "dataType": "valid", "defaultValue": "valid", "name": "valid", "extra": "attribute"}
    ]
    args = {"variableEntries": variable_entries}

    # Act
    exception_thrown = None
    try:
        validation_helpers.check_variable_entries_are_valid(args)
    except exceptions.InvalidRequest as invalid_request_exception:
        exception_thrown = invalid_request_exception

    # Assert
    assert exception_thrown is not None
    assert "unrecognized attributes" in f"{exception_thrown}"


def test_validate_event_variables_attributes_inline_without_name():
    # Arrange
    event_variables = [
        EventVariable(
            Inline=True,
            Name=None,
            Arn="some_arn",
            DataSource="some_data_source",
            DataType="some_data_type",
            DefaultValue="some_default_value",
            Description="some_description",
            Tags=None,
            CreatedTime="some_time_created",
            LastUpdatedTime="some_time_updated",
            VariableType="some_variable_type",
        )
    ]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_event_variables_attributes(event_variables)
    except exceptions.InvalidRequest as invalid_request_exception:
        exception_thrown = invalid_request_exception

    # Assert
    assert exception_thrown is not None
    assert "inline event variables must include Name" in f"{exception_thrown}"


def test_validate_event_variables_attributes_referenced_without_arn():
    # Arrange
    event_variables = [
        EventVariable(
            Inline=False,
            Name="some_name",
            Arn=None,
            DataSource="some_data_source",
            DataType="some_data_type",
            DefaultValue="some_default_value",
            Description="some_description",
            Tags=None,
            CreatedTime="some_time_created",
            LastUpdatedTime="some_time_updated",
            VariableType="some_variable_type",
        )
    ]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_event_variables_attributes(event_variables)
    except exceptions.InvalidRequest as invalid_request_exception:
        exception_thrown = invalid_request_exception

    # Assert
    assert exception_thrown is not None
    assert "non-inline event variables must include Arn" in f"{exception_thrown}"


def test_validate_event_variables_attributes_happy_case():
    # Arrange
    event_variables = [
        EventVariable(
            Inline=True,
            Name="some_name",
            Arn=None,
            DataSource="some_data_source",
            DataType="some_data_type",
            DefaultValue="some_default_value",
            Description="some_description",
            Tags=None,
            CreatedTime="some_time_created",
            LastUpdatedTime="some_time_updated",
            VariableType="some_variable_type",
        ),
        EventVariable(
            Inline=False,
            Name=None,
            Arn=FAKE_VALID_ARN,
            DataSource="some_data_source",
            DataType="some_data_type",
            DefaultValue="some_default_value",
            Description="some_description",
            Tags=None,
            CreatedTime="some_time_created",
            LastUpdatedTime="some_time_updated",
            VariableType="some_variable_type",
        ),
    ]

    # Act
    vars_by_name, var_names = validation_helpers.validate_event_variables_attributes(event_variables)

    # Assert
    assert len(vars_by_name) == 2
    assert "some_name" in vars_by_name
    assert util.extract_name_from_arn(FAKE_VALID_ARN) in vars_by_name
    assert len(var_names) == 2
    assert "some_name" in var_names
    assert util.extract_name_from_arn(FAKE_VALID_ARN) in var_names


def test_validate_missing_variables_for_create_reference_missing():
    # Arrange
    missing_var_arn = "arn:aws:frauddetector:us-west-1:123123123123:variable/missing_var"
    errors = [{"name": "missing_var"}]
    vars_by_name = {
        "missing_var": EventVariable(
            Inline=False,
            Name="missing_var",
            Arn=missing_var_arn,
            DataSource="some_data_source",
            DataType="some_data_type",
            DefaultValue="some_default_value",
            Description="some_description",
            Tags=None,
            CreatedTime="some_time_created",
            LastUpdatedTime="some_time_updated",
            VariableType="some_variable_type",
        )
    }

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_missing_variables_for_create(errors, vars_by_name)
    except exceptions.NotFound as rnf_exception:
        exception_thrown = rnf_exception

    # Assert
    assert exception_thrown is not None
    assert "event_variable" in f"{exception_thrown}"
    assert missing_var_arn in f"{exception_thrown}"
    assert "was not found" in f"{exception_thrown}"
