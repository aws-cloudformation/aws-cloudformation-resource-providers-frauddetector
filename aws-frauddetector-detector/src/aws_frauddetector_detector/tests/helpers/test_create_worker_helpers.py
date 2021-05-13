from aws_frauddetector_detector.helpers import (
    create_worker_helpers,
    validation_helpers,
)
from aws_frauddetector_detector import models
from cloudformation_cli_python_lib import (
    exceptions,
)
from .. import unit_test_utils
from unittest.mock import MagicMock


def test_validate_dependencies_for_detector_create_happy_case(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1


def test_validate_dependencies_for_detector_create_external_model_dne_throws_exception(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found"))]
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": []})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models

    # Act
    exception_thrown = None
    try:
        create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1
    assert exception_thrown is not None


def test_validate_dependencies_for_detector_create_with_referenced_dependencies(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model_with_references()
    get_outcomes_response = {"outcomes": [unit_test_utils.FAKE_OUTCOME]}
    mock_check_get_outcomes = MagicMock(return_value=(True, get_outcomes_response))
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    mock_check_get_event_types = MagicMock(return_value=(True, get_event_types_response))

    mock_check_get_variables = MagicMock()
    mock_check_get_labels = MagicMock()
    mock_check_get_entity_types = MagicMock()

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 1
    assert mock_check_get_event_types.call_count == 1
    assert mock_check_get_variables.call_count == 0
    assert mock_check_get_labels.call_count == 0
    assert mock_check_get_entity_types.call_count == 0


def test_validate_dependencies_for_detector_create_with_inline_event_type_with_referenced_dependencies(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.EventType = unit_test_utils.create_fake_inline_event_type_with_referenced_dependencies()
    get_outcomes_response = {"outcomes": [unit_test_utils.FAKE_OUTCOME]}
    mock_check_get_outcomes = MagicMock(return_value=(True, get_outcomes_response))
    get_event_types_response = {"eventTypes": [unit_test_utils.FAKE_EVENT_TYPE]}
    mock_check_get_event_types = MagicMock(return_value=(True, get_event_types_response))
    get_variables_response = {
        "variables": [
            unit_test_utils.FAKE_IP_VARIABLE,
            unit_test_utils.FAKE_EMAIL_VARIABLE,
        ]
    }
    mock_check_get_variables = MagicMock(return_value=(True, get_variables_response))
    get_labels_response = {"labels": [unit_test_utils.FAKE_FRAUD_LABEL, unit_test_utils.FAKE_LEGIT_LABEL]}
    mock_check_get_labels = MagicMock(return_value=(True, get_labels_response))
    get_entity_types_response = {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]}
    mock_check_get_entity_types = MagicMock(return_value=(True, get_entity_types_response))

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1


def test_validate_dependencies_for_detector_create_happy_case_with_model_version(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_model_version = MagicMock(return_value=(True, {"status": "ACTIVE"}))
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models
    monkeypatch.setattr(validation_helpers, "check_if_get_model_version_succeeds", mock_check_get_model_version)

    # Act
    create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1
    assert mock_check_get_model_version.call_count == 1


def test_validate_dependencies_for_detector_create_with_invalid_model_version_arn(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn="invalid_arn")]
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_model_version = MagicMock(return_value=(False, {"status": "ACTIVE"}))
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models
    monkeypatch.setattr(validation_helpers, "check_if_get_model_version_succeeds", mock_check_get_model_version)

    # Act
    exception_thrown = None
    try:
        create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1
    assert mock_check_get_model_version.call_count == 0  # get_model_version should not be called
    assert exception_thrown is not None
    assert str(exception_thrown) == "Unexpected ARN provided in AssociatedModels: {}".format(
        fake_model.AssociatedModels[0].Arn
    )


def test_validate_dependencies_for_detector_create_model_version_not_active(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_model_version = MagicMock(return_value=(True, {"status": "TRAINING_IN_PROGRESS"}))
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models
    monkeypatch.setattr(validation_helpers, "check_if_get_model_version_succeeds", mock_check_get_model_version)

    # Act
    exception_thrown = None
    try:
        create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1
    assert mock_check_get_model_version.call_count == 1
    assert exception_thrown is not None
    assert str(exception_thrown) == "Specified model must be in status:ACTIVE, ModelVersion arn='{}'".format(
        unit_test_utils.FAKE_MODEL_VERSION_ARN
    )


def test_validate_dependencies_for_detector_create_get_model_version_fails(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    mock_check_get_outcomes = MagicMock()
    mock_check_get_event_types = MagicMock()
    mock_check_get_model_version = MagicMock(return_value=(False, {"status": "ACTIVE"}))
    mock_check_get_variables = MagicMock(return_value=(False, None))
    mock_check_get_labels = MagicMock(return_value=(False, None))
    mock_check_get_entity_types = MagicMock(return_value=(False, None))
    mock_get_external_models = MagicMock(return_value={"externalModels": [unit_test_utils.FAKE_EXTERNAL_MODEL]})

    monkeypatch.setattr(validation_helpers, "check_if_get_outcomes_succeeds", mock_check_get_outcomes)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_get_event_types,
    )
    monkeypatch.setattr(validation_helpers, "check_if_get_variables_succeeds", mock_check_get_variables)
    monkeypatch.setattr(validation_helpers, "check_if_get_labels_succeeds", mock_check_get_labels)
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_get_entity_types,
    )
    mock_afd_client.get_external_models = mock_get_external_models
    monkeypatch.setattr(validation_helpers, "check_if_get_model_version_succeeds", mock_check_get_model_version)

    # Act
    exception_thrown = None
    try:
        create_worker_helpers.validate_dependencies_for_detector_create(mock_afd_client, fake_model)
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert mock_check_get_outcomes.call_count == 0
    assert mock_check_get_event_types.call_count == 0
    assert mock_check_get_variables.call_count == 2
    assert mock_check_get_labels.call_count == 2
    assert mock_check_get_entity_types.call_count == 1
    assert mock_get_external_models.call_count == 1
    assert mock_check_get_model_version.call_count == 1
    assert exception_thrown is not None
