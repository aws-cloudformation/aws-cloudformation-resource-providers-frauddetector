from aws_frauddetector_detector.helpers import (
    update_worker_helpers,
    validation_helpers,
    api_helpers,
    common_helpers,
    model_helpers,
)
from aws_frauddetector_detector import models
from botocore.exceptions import ClientError
from cloudformation_cli_python_lib import (
    exceptions,
)
from .. import unit_test_utils
from unittest.mock import MagicMock, ANY

# VALIDATION
mock_check_if_get_event_types_succeeds = MagicMock()
mock_check_if_get_variables_succeeds = MagicMock()
mock_check_if_get_entity_types_succeeds = MagicMock()
mock_check_if_get_labels_succeeds = MagicMock()

# API
mock_call_create_detector_version = MagicMock()
mock_call_create_rule = MagicMock()
mock_call_delete_detector_version = MagicMock()
mock_call_delete_rule = MagicMock()
mock_call_delete_outcome = MagicMock()
mock_call_delete_variable = MagicMock()
mock_call_delete_entity_type = MagicMock()
mock_call_delete_label = MagicMock()
mock_call_describe_detector = MagicMock()
mock_call_get_rules = MagicMock()
mock_call_get_detector_version = MagicMock()
mock_call_put_outcome = MagicMock()
mock_call_update_detector_version = MagicMock()
mock_call_update_detector_version_status = MagicMock()
mock_call_update_rule_version = MagicMock()
mock_call_update_variable = MagicMock()

# COMMON
mock_update_tags = MagicMock()
mock_create_inline_event_variable = MagicMock()
mock_put_inline_entity_type = MagicMock()
mock_put_inline_label = MagicMock()

# MODEL
mock_get_outcomes_model_for_given_outcome_names = None


def test_validate_dependencies_for_detector_update_inline_eventtype_success(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_previous_model = unit_test_utils.create_fake_model()
    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    update_worker_helpers.validate_dependencies_for_detector_update(mock_afd_client, fake_model, fake_previous_model)

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0


def test_validate_dependencies_for_detector_update_external_model_dne_throws_exception(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found"))]
    fake_previous_model = unit_test_utils.create_fake_model()
    mock_check_if_get_event_types_succeeds = MagicMock()
    mock_get_external_models = MagicMock(return_value={"externalModels": []})
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )
    mock_afd_client.get_external_models = mock_get_external_models

    # Act
    exception_thrown = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert mock_get_external_models.call_count == 1
    assert exception_thrown is not None


def test_validate_dependencies_for_detector_update_model_version_happy_case(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    fake_previous_model = unit_test_utils.create_fake_model()

    mock_check_get_model_version = MagicMock(return_value=unit_test_utils.create_fake_model_version())
    mock_afd_client.get_model_version = mock_check_get_model_version
    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    update_worker_helpers.validate_dependencies_for_detector_update(mock_afd_client, fake_model, fake_previous_model)

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert mock_check_get_model_version.call_count == 1


def test_validate_dependencies_for_detector_update_model_version_invalid_arn(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn="invalid_arn")]
    fake_previous_model = unit_test_utils.create_fake_model()
    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    exception_thrown = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert exception_thrown is not None
    assert str(exception_thrown) == "Unexpected ARN provided in AssociatedModels: {}".format(
        fake_model.AssociatedModels[0].Arn
    )


def test_validate_dependencies_for_detector_update_model_version_rnf(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    fake_previous_model = unit_test_utils.create_fake_model()

    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    mock_check_get_model_version = MagicMock()
    mock_check_get_model_version.side_effect = ClientError({"Code": "", "Message": ""}, "get_model_version")
    mock_afd_client.get_model_version = mock_check_get_model_version

    # Act
    exception_thrown = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.NotFound as e:
        exception_thrown = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert mock_check_get_model_version.call_count == 1
    assert exception_thrown is not None


def test_validate_dependencies_for_detector_update_model_version_not_active(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.AssociatedModels = [models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN)]
    fake_previous_model = unit_test_utils.create_fake_model()

    return_value = unit_test_utils.create_fake_model_version()
    return_value["status"] = "TRAINING_IN_PROGRESS"
    mock_check_get_model_version = MagicMock(return_value=return_value)
    mock_afd_client.get_model_version = mock_check_get_model_version

    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    exception_thrown = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.InvalidRequest as e:
        exception_thrown = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert mock_check_get_model_version.call_count == 1
    assert exception_thrown is not None
    assert str(exception_thrown) == "Specified model must be in status:ACTIVE, ModelVersion arn='{}'".format(
        unit_test_utils.FAKE_MODEL_VERSION_ARN
    )


def test_validate_dependencies_for_detector_update_referenced_eventtype_success(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model_with_references()
    fake_previous_model = unit_test_utils.create_fake_model_with_references()

    mock_check_if_get_event_types_succeeds = MagicMock(return_value=(True, {}))
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    update_worker_helpers.validate_dependencies_for_detector_update(mock_afd_client, fake_model, fake_previous_model)

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 1


def test_validate_dependencies_for_detector_update_referenced_eventtype_dne_fails(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model_with_references()
    fake_previous_model = unit_test_utils.create_fake_model_with_references()
    mock_check_if_get_event_types_succeeds = MagicMock(return_value=(False, {}))
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    thrown_exception = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.NotFound as e:
        thrown_exception = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 1
    assert thrown_exception is not None


def test_validate_dependencies_for_detector_update_different_eventtype_name_fails(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model_with_references()
    fake_previous_model = unit_test_utils.create_fake_model_with_references()
    fake_previous_model.EventType.Name = "different"
    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    thrown_exception = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.InvalidRequest as e:
        thrown_exception = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert thrown_exception is not None


def test_validate_dependencies_for_detector_update_different_eventtype_inline_fails(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_previous_model = unit_test_utils.create_fake_model_with_references()
    fake_model.EventType.Name = fake_previous_model.EventType.Name = "same"
    mock_check_if_get_event_types_succeeds = MagicMock()
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )

    # Act
    thrown_exception = None
    try:
        update_worker_helpers.validate_dependencies_for_detector_update(
            mock_afd_client, fake_model, fake_previous_model
        )
    except exceptions.InvalidRequest as e:
        thrown_exception = e

    # Assert
    assert mock_check_if_get_event_types_succeeds.call_count == 0
    assert thrown_exception is not None


def test_update_rules_and_inline_outcomes_for_detector_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_previous_model = unit_test_utils.create_fake_model()
    fake_model.Description = "different description"  # only model difference

    global mock_call_get_rules
    global mock_get_outcomes_model_for_given_outcome_names

    get_rules_response = {"ruleDetails": [unit_test_utils.FAKE_RULE_DETAIL]}
    mock_call_get_rules = MagicMock(return_value=get_rules_response)
    mock_get_outcomes_model_for_given_outcome_names = MagicMock(
        return_value=[unit_test_utils.create_fake_outcome(True)]
    )

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    (
        unused_rule_versions,
        unused_inline_outcomes,
    ) = update_worker_helpers.update_rules_and_inline_outcomes_for_detector_update(
        mock_afd_client, fake_model, fake_previous_model
    )

    # Assert
    assert len(unused_rule_versions) == 1  # currently, we always update rule version for simplicity
    assert len(unused_inline_outcomes) == 0  # outcome is not updated


def test_update_detector_version_for_detector_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_previous_model = unit_test_utils.create_fake_model()
    fake_model.Description = "different description"  # only model difference

    global mock_call_describe_detector
    global mock_call_get_detector_version
    global mock_call_create_detector_version

    fake_dv_summary_with_draft_status = {
        "description": unit_test_utils.FAKE_DESCRIPTION,
        "detectorVersionId": unit_test_utils.FAKE_VERSION_ID,
        "lastUpdatedTime": unit_test_utils.FAKE_TIME,
        "status": unit_test_utils.FAKE_DRAFT_DV_STATUS,
    }

    describe_detector_response = {
        "detectorVersionSummaries": [
            fake_dv_summary_with_draft_status,
            unit_test_utils.FAKE_NEW_DETECTOR_VERSION,
        ]
    }
    mock_call_describe_detector = MagicMock(return_value=describe_detector_response)
    mock_call_create_detector_version = MagicMock(return_value=None)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    detector_versions_to_delete = update_worker_helpers.update_detector_version_for_detector_update(
        mock_afd_client, fake_model, fake_previous_model
    )

    # Assert
    assert mock_call_describe_detector.call_count == 2
    assert len(detector_versions_to_delete) == 1  # we create a new DV when existing DV is not DRAFT
    mock_call_create_detector_version.assert_called_once_with(
        frauddetector_client=mock_afd_client,
        detector_id=fake_model.DetectorId,
        rules=ANY,
        rule_execution_mode=fake_model.RuleExecutionMode,
        model_versions=[],
        external_model_endpoints=[],
        detector_version_description=fake_model.Description,
        detector_version_tags=ANY,
    )


def test_update_detector_version_for_detector_update_draft_dv(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.DetectorVersionStatus = unit_test_utils.FAKE_DRAFT_DV_STATUS
    fake_previous_model = unit_test_utils.create_fake_model()
    fake_previous_model.DetectorVersionStatus = unit_test_utils.FAKE_DRAFT_DV_STATUS
    fake_model.Description = "different description"  # only model difference

    global mock_call_describe_detector
    global mock_call_get_detector_version
    global mock_call_update_detector_version

    describe_detector_response = {"detectorVersionSummaries": [unit_test_utils.FAKE_DETECTOR_VERSION]}
    get_detector_version_response = unit_test_utils.FAKE_DETECTOR_VERSION
    mock_call_describe_detector = MagicMock(return_value=describe_detector_response)
    mock_call_get_detector_version = MagicMock(return_value=get_detector_version_response)
    mock_call_update_detector_version = MagicMock(return_value=None)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    detector_versions_to_delete = update_worker_helpers.update_detector_version_for_detector_update(
        mock_afd_client, fake_model, fake_previous_model
    )

    # Assert
    assert len(detector_versions_to_delete) == 0  # we do NOT create a new DV when existing DV is DRAFT
    mock_call_update_detector_version.assert_called_once_with(
        frauddetector_client=mock_afd_client,
        detector_id=fake_model.DetectorId,
        detector_version_id=ANY,
        rules=ANY,
        rule_execution_mode=fake_model.RuleExecutionMode,
        model_versions=[],
        external_model_endpoints=[],
        detector_version_description=ANY,
    )


def test_update_detector_version_for_detector_update_with_associated_models(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_previous_model = unit_test_utils.create_fake_model()

    # 2 model differences
    fake_model.Description = "different description"
    fake_model.AssociatedModels = [
        models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN),
        models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found")),
    ]

    global mock_call_describe_detector
    global mock_call_get_detector_version
    global mock_call_create_detector_version

    fake_dv_summary_with_draft_status = {
        "description": unit_test_utils.FAKE_DESCRIPTION,
        "detectorVersionId": unit_test_utils.FAKE_VERSION_ID,
        "lastUpdatedTime": unit_test_utils.FAKE_TIME,
        "status": unit_test_utils.FAKE_DRAFT_DV_STATUS,
    }

    describe_detector_response = {
        "detectorVersionSummaries": [
            fake_dv_summary_with_draft_status,
            unit_test_utils.FAKE_NEW_DETECTOR_VERSION,
        ]
    }
    mock_call_describe_detector = MagicMock(return_value=describe_detector_response)
    mock_call_create_detector_version = MagicMock(return_value=None)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    detector_versions_to_delete = update_worker_helpers.update_detector_version_for_detector_update(
        mock_afd_client, fake_model, fake_previous_model
    )

    # Assert
    assert mock_call_describe_detector.call_count == 2
    assert len(detector_versions_to_delete) == 1  # we create a new DV when existing DV is not DRAFT
    mock_call_create_detector_version.assert_called_once_with(
        frauddetector_client=mock_afd_client,
        detector_id=fake_model.DetectorId,
        rules=ANY,
        rule_execution_mode=fake_model.RuleExecutionMode,
        model_versions=unit_test_utils.FAKE_MODEL_VERSION_LIST,
        external_model_endpoints=[unit_test_utils.FAKE_NAME],
        detector_version_description=fake_model.Description,
        detector_version_tags=ANY,
    )


def test_update_detector_version_for_detector_update_draft_dv_with_associated_models(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    fake_model = unit_test_utils.create_fake_model()
    fake_model.DetectorVersionStatus = unit_test_utils.FAKE_DRAFT_DV_STATUS
    fake_previous_model = unit_test_utils.create_fake_model()
    fake_previous_model.DetectorVersionStatus = unit_test_utils.FAKE_DRAFT_DV_STATUS

    # 2 model differences
    fake_model.Description = "different description"
    fake_model.AssociatedModels = [
        models.Model(Arn=unit_test_utils.FAKE_MODEL_VERSION_ARN),
        models.Model(Arn=unit_test_utils.FAKE_EXTERNAL_MODEL.get("arn", "not/found")),
    ]

    global mock_call_describe_detector
    global mock_call_get_detector_version
    global mock_call_update_detector_version

    describe_detector_response = {"detectorVersionSummaries": [unit_test_utils.FAKE_DETECTOR_VERSION]}
    get_detector_version_response = unit_test_utils.FAKE_DETECTOR_VERSION
    mock_call_describe_detector = MagicMock(return_value=describe_detector_response)
    mock_call_get_detector_version = MagicMock(return_value=get_detector_version_response)
    mock_call_update_detector_version = MagicMock(return_value=None)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    detector_versions_to_delete = update_worker_helpers.update_detector_version_for_detector_update(
        mock_afd_client, fake_model, fake_previous_model
    )

    # Assert
    assert len(detector_versions_to_delete) == 0  # we do NOT create a new DV when existing DV is DRAFT
    mock_call_update_detector_version.assert_called_once_with(
        frauddetector_client=mock_afd_client,
        detector_id=fake_model.DetectorId,
        detector_version_id=ANY,
        rules=ANY,
        rule_execution_mode=fake_model.RuleExecutionMode,
        model_versions=unit_test_utils.FAKE_MODEL_VERSION_LIST,
        external_model_endpoints=[unit_test_utils.FAKE_NAME],
        detector_version_description=fake_model.Description,
    )


def test_delete_unused_detector_versions_for_detector_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()

    global mock_call_delete_detector_version

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    update_worker_helpers.delete_unused_detector_versions_for_detector_update(mock_afd_client, {("1", "2"), ("3", "4")})

    # Assert
    assert mock_call_delete_detector_version.call_count == 2  # we sent 2 tuples, so call delete DV twice


def test_delete_unused_rules_for_detector_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()

    global mock_call_delete_rule

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    update_worker_helpers.delete_unused_rules_for_detector_update(
        mock_afd_client, "detector_id", {("1", "2"), ("3", "4")}
    )

    # Assert
    assert mock_call_delete_rule.call_count == 2  # we sent 2 tuples, so call delete rule twice


def test_delete_unused_inline_outcomes_for_detector_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()

    global mock_call_delete_outcome

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    update_worker_helpers.delete_unused_inline_outcomes_for_detector_update(mock_afd_client, {"1", "2"})

    # Assert
    assert mock_call_delete_outcome.call_count == 2  # we sent 2 outcome names, so call delete outcome twice


def test_validate_dependencies_for_inline_event_type_update(monkeypatch):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    event_type_model = unit_test_utils.create_fake_event_type()
    previous_event_type_model = unit_test_utils.create_fake_event_type()
    event_type_model.Description = "different"  # only difference

    global mock_call_delete_variable
    global mock_call_delete_entity_type
    global mock_call_delete_label
    global mock_put_inline_label
    global mock_put_inline_entity_type
    global mock_create_inline_event_variable
    global mock_call_update_variable
    global mock_update_tags

    global mock_check_if_get_variables_succeeds
    global mock_check_if_get_entity_types_succeeds
    global mock_check_if_get_labels_succeeds

    mock_check_if_get_variables_succeeds_response = (
        True,
        {"variables": [unit_test_utils.FAKE_IP_VARIABLE]},
    )
    mock_check_if_get_variables_succeeds = MagicMock(return_value=mock_check_if_get_variables_succeeds_response)

    mock_check_if_get_entity_types_succeeds_response = (
        True,
        {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]},
    )
    mock_check_if_get_entity_types_succeeds = MagicMock(return_value=mock_check_if_get_entity_types_succeeds_response)

    mock_check_if_get_labels_succeeds_response = (
        True,
        {"labels": [unit_test_utils.FAKE_LEGIT_LABEL]},
    )
    mock_check_if_get_labels_succeeds = MagicMock(return_value=mock_check_if_get_labels_succeeds_response)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    update_worker_helpers.validate_dependencies_for_inline_event_type_update(
        mock_afd_client, event_type_model, previous_event_type_model
    )

    # Assert (we did not change any event type dependencies, do not delete anything)
    assert mock_call_delete_variable.call_count == 0
    assert mock_call_delete_entity_type.call_count == 0
    assert mock_call_delete_label.call_count == 0
    assert mock_put_inline_label.call_count == 2
    assert mock_put_inline_entity_type.call_count == 1
    assert mock_create_inline_event_variable.call_count == 0
    assert mock_call_update_variable.call_count == 2
    assert mock_update_tags.call_count == 8


def test_validate_dependencies_for_inline_event_type_update_referenced_dependencies(
    monkeypatch,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    event_type_model = unit_test_utils.create_fake_inline_event_type_with_referenced_dependencies()
    previous_event_type_model = unit_test_utils.create_fake_inline_event_type_with_referenced_dependencies()
    event_type_model.Description = "different"  # only difference

    global mock_call_delete_variable
    global mock_call_delete_entity_type
    global mock_call_delete_label
    global mock_put_inline_label
    global mock_put_inline_entity_type
    global mock_create_inline_event_variable
    global mock_call_update_variable
    global mock_update_tags

    global mock_check_if_get_variables_succeeds
    global mock_check_if_get_entity_types_succeeds
    global mock_check_if_get_labels_succeeds

    mock_check_if_get_variables_succeeds_response = (
        True,
        {"variables": [unit_test_utils.FAKE_IP_VARIABLE]},
    )
    mock_check_if_get_variables_succeeds = MagicMock(return_value=mock_check_if_get_variables_succeeds_response)

    mock_check_if_get_entity_types_succeeds_response = (
        True,
        {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]},
    )
    mock_check_if_get_entity_types_succeeds = MagicMock(return_value=mock_check_if_get_entity_types_succeeds_response)

    mock_check_if_get_labels_succeeds_response = (
        True,
        {"labels": [unit_test_utils.FAKE_LEGIT_LABEL]},
    )
    mock_check_if_get_labels_succeeds = MagicMock(return_value=mock_check_if_get_labels_succeeds_response)

    _setup_monkeypatch_for_update_workers(monkeypatch)

    # Act
    update_worker_helpers.validate_dependencies_for_inline_event_type_update(
        mock_afd_client, event_type_model, previous_event_type_model
    )

    # Assert (we did not change any event type dependencies, do not delete anything)
    assert mock_call_delete_variable.call_count == 0
    assert mock_call_delete_entity_type.call_count == 0
    assert mock_call_delete_label.call_count == 0
    assert mock_put_inline_label.call_count == 2  # we call put label regardless for simplicity
    assert mock_put_inline_entity_type.call_count == 1  # we call put entity type regardless for simplicity
    assert mock_create_inline_event_variable.call_count == 0
    assert mock_call_update_variable.call_count == 2  # we call update variable regardless for simplicity
    assert mock_update_tags.call_count == 8


def _setup_monkeypatch_for_update_workers(monkeypatch):
    """
    This is an easy way to make sure all the other helpers called in update_worker_helpers are mocks
    """
    # VALIDATION
    global mock_check_if_get_event_types_succeeds
    global mock_check_if_get_variables_succeeds
    global mock_check_if_get_entity_types_succeeds
    global mock_check_if_get_labels_succeeds

    # API
    global mock_call_create_detector_version
    global mock_call_create_rule
    global mock_call_delete_detector_version
    global mock_call_delete_rule
    global mock_call_delete_outcome
    global mock_call_delete_variable
    global mock_call_delete_entity_type
    global mock_call_delete_label
    global mock_call_describe_detector
    global mock_call_get_rules
    global mock_call_get_detector_version
    global mock_call_put_outcome
    global mock_call_update_detector_version
    global mock_call_update_detector_version_status
    global mock_call_update_rule_version
    global mock_call_update_variable

    # COMMON
    global mock_update_tags
    global mock_create_inline_event_variable
    global mock_put_inline_entity_type
    global mock_put_inline_label

    # MODEL
    global mock_get_outcomes_model_for_given_outcome_names

    monkeypatch.setattr(api_helpers, "call_create_detector_version", mock_call_create_detector_version)
    monkeypatch.setattr(api_helpers, "call_create_rule", mock_call_create_rule)
    monkeypatch.setattr(api_helpers, "call_delete_detector_version", mock_call_delete_detector_version)
    monkeypatch.setattr(api_helpers, "call_delete_rule", mock_call_delete_rule)
    monkeypatch.setattr(api_helpers, "call_delete_outcome", mock_call_delete_outcome)
    monkeypatch.setattr(api_helpers, "call_delete_variable", mock_call_delete_variable)
    monkeypatch.setattr(api_helpers, "call_delete_entity_type", mock_call_delete_entity_type)
    monkeypatch.setattr(api_helpers, "call_delete_label", mock_call_delete_label)
    monkeypatch.setattr(api_helpers, "call_describe_detector", mock_call_describe_detector)
    monkeypatch.setattr(api_helpers, "call_get_rules", mock_call_get_rules)
    monkeypatch.setattr(api_helpers, "call_get_detector_version", mock_call_get_detector_version)
    monkeypatch.setattr(api_helpers, "call_put_outcome", mock_call_put_outcome)
    monkeypatch.setattr(api_helpers, "call_update_detector_version", mock_call_update_detector_version)
    monkeypatch.setattr(
        api_helpers,
        "call_update_detector_version_status",
        mock_call_update_detector_version_status,
    )
    monkeypatch.setattr(api_helpers, "call_update_rule_version", mock_call_update_rule_version)
    monkeypatch.setattr(api_helpers, "call_update_variable", mock_call_update_variable)

    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_event_types_succeeds",
        mock_check_if_get_event_types_succeeds,
    )
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_variables_succeeds",
        mock_check_if_get_variables_succeeds,
    )
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_entity_types_succeeds",
        mock_check_if_get_entity_types_succeeds,
    )
    monkeypatch.setattr(
        validation_helpers,
        "check_if_get_labels_succeeds",
        mock_check_if_get_labels_succeeds,
    )

    monkeypatch.setattr(common_helpers, "update_tags", mock_update_tags)
    monkeypatch.setattr(
        common_helpers,
        "create_inline_event_variable",
        mock_create_inline_event_variable,
    )
    monkeypatch.setattr(common_helpers, "put_inline_entity_type", mock_put_inline_entity_type)
    monkeypatch.setattr(common_helpers, "put_inline_label", mock_put_inline_label)

    monkeypatch.setattr(
        model_helpers,
        "get_outcomes_model_for_given_outcome_names",
        mock_get_outcomes_model_for_given_outcome_names,
    )
