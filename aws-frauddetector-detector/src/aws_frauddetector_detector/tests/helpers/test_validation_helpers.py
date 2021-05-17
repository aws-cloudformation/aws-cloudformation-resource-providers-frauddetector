from ...helpers import validation_helpers
from ... import models
from botocore.exceptions import ClientError
from unittest.mock import MagicMock
from .. import unit_test_utils

from cloudformation_cli_python_lib import (
    exceptions,
)


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


def test_validate_external_models_for_detector_model_model_exists():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})
    mock_afd_client.get_external_models = mock_get_external_models
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found"))]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_external_models_for_detector_model(mock_afd_client, fake_model)
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert exception_thrown is None


def test_validate_external_models_for_detector_model_model_dne_throw_exception():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_get_external_models = MagicMock(return_value={"externalModels": []})
    mock_afd_client.get_external_models = mock_get_external_models
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found"))]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_external_models_for_detector_model(mock_afd_client, fake_model)
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert exception_thrown is not None


def test_validate_model_versions_for_detector_model_happy_case():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_check_get_model_version = MagicMock(return_value=unit_test_utils.create_fake_model_version())
    mock_afd_client.get_model_version = mock_check_get_model_version

    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]

    # Act
    validation_helpers.validate_model_versions_for_detector_model(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_model_version.call_count == 1


def test_validate_model_versions_for_detector_model_get_model_version_throws_rnf():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    mock_check_get_model_version = MagicMock()
    mock_check_get_model_version.side_effect = ClientError({"Code": "", "Message": ""}, "get_model_version")
    mock_afd_client.get_model_version = mock_check_get_model_version

    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_model_versions_for_detector_model(mock_afd_client, fake_model)
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_model_version.call_count == 1
    assert exception_thrown is not None


def test_validate_model_versions_for_detector_model_invalid_arn():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_check_get_model_version = MagicMock(return_value=unit_test_utils.create_fake_model_version())
    mock_afd_client.get_model_version = mock_check_get_model_version

    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn="invalid_arn")]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_model_versions_for_detector_model(mock_afd_client, fake_model)
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_model_version.call_count == 0  # exception thrown before get_model_version check
    assert exception_thrown is not None


def test_validate_model_versions_for_detector_model_model_version_not_active():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    return_value = unit_test_utils.create_fake_model_version()
    return_value["status"] = "TRAINING_IN_PROGRESS"
    mock_check_get_model_version = MagicMock(return_value=return_value)
    mock_afd_client.get_model_version = mock_check_get_model_version

    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]

    # Act
    exception_thrown = None
    try:
        validation_helpers.validate_model_versions_for_detector_model(mock_afd_client, fake_model)
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_model_version.call_count == 1  # exception thrown after get_model_version check
    assert exception_thrown is not None
