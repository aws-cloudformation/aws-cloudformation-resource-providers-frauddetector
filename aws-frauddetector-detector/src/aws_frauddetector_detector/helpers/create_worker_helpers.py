import logging
from typing import List

from cloudformation_cli_python_lib import (
    exceptions,
)

from . import validation_helpers, common_helpers, model_helpers, api_helpers, util
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_dependencies_for_detector_create(afd_client, model: models.ResourceModel):
    _validate_event_type_for_detector_create(afd_client, model)
    _validate_rules_for_detector_create(afd_client, model)
    validation_helpers.validate_external_models_for_detector_model(afd_client, model)


def create_rules_for_detector_resource(afd_client, model: models.ResourceModel) -> List[dict]:
    rule_dicts = []
    for rule in model.Rules:
        rule_dict = model_helpers.create_rule_for_rule_model(afd_client, rule, model)
        rule_dicts.append(rule_dict)
    return rule_dicts


def create_detector_version_for_detector_resource(
    afd_client, model: models.ResourceModel, rule_dicts: List[dict]
) -> dict:
    # abstracted DVs will have the same tags as the Detector resource provider
    tags = model_helpers.get_tags_from_tag_models(model.Tags)
    external_models = model_helpers.get_external_model_endpoints_from_model(model)
    # TODO: support model versions
    return api_helpers.call_create_detector_version(
        frauddetector_client=afd_client,
        detector_id=model.DetectorId,
        rules=rule_dicts,
        rule_execution_mode=model.RuleExecutionMode,
        model_versions=None,
        external_model_endpoints=external_models,
        detector_version_description=model.Description,
        detector_version_tags=tags,
    )


def _validate_outcomes_for_rule(afd_client, rule_model: models.Rule):
    for outcome_model in rule_model.Outcomes:
        if outcome_model.Inline:
            _create_inline_outcome(afd_client, outcome_model)
        else:
            outcome_name = util.extract_name_from_arn(outcome_model.Arn)
            get_outcomes_worked, _ = validation_helpers.check_if_get_outcomes_succeeds(
                frauddetector_client=afd_client, outcome_name=outcome_name
            )
            if not get_outcomes_worked:
                raise exceptions.NotFound("non-inline outcome", outcome_name)


def _create_inline_outcome(afd_client, outcome_model: models.Outcome):
    tags = model_helpers.get_tags_from_tag_models(outcome_model.Tags)
    api_helpers.call_put_outcome(
        frauddetector_client=afd_client,
        outcome_name=outcome_model.Name,
        outcome_tags=tags,
        outcome_description=outcome_model.Description,
    )


def _validate_event_type_for_detector_create(afd_client, model: models.ResourceModel):
    event_type_model = model.EventType
    if event_type_model.Inline:
        _validate_dependencies_for_inline_event_type_create(afd_client, event_type_model)
        common_helpers.put_event_type_for_detector_model(frauddetector_client=afd_client, detector_model=model)
    else:
        _validate_referenced_event_type(afd_client, event_type_model)


def _validate_referenced_event_type(afd_client, event_type_model: models.EventType):
    # check if event type exists, that's all.
    event_type_name = util.extract_name_from_arn(event_type_model.Arn)
    get_event_types_worked, _ = validation_helpers.check_if_get_event_types_succeeds(afd_client, event_type_name)
    if not get_event_types_worked:
        raise exceptions.NotFound("non-inline event_type", event_type_name)


def _validate_rules_for_detector_create(afd_client, model: models.ResourceModel):
    for rule in model.Rules:
        _validate_rule_for_detector_create(afd_client, model, rule)


def _validate_rule_for_detector_create(afd_client, model: models.ResourceModel, rule: models.Rule):
    if model.DetectorId != rule.DetectorId:
        raise exceptions.InvalidRequest(
            f"Rule {rule.RuleId} detector id {rule.DetectorId} does not match detector id {model.DetectorId}!"
        )
    _validate_outcomes_for_rule(afd_client, rule)


def _validate_dependencies_for_inline_event_type_create(afd_client, event_type_model: models.EventType):
    _validate_event_variables_for_event_type_create(afd_client, event_type_model)
    _validate_entity_types_for_create(afd_client, event_type_model)
    _validate_labels_for_create(afd_client, event_type_model)


def _validate_event_variables_for_event_type_create(afd_client, event_type_model: models.EventType):
    for event_variable in event_type_model.EventVariables:
        _validate_event_variable_for_create(afd_client, event_variable)


def _validate_event_variable_for_create(afd_client, event_variable):
    if event_variable.Inline:
        _validate_inline_event_variable_for_create(afd_client, event_variable)
    else:
        _validate_referenced_event_variable_for_create(afd_client, event_variable)


def _validate_referenced_event_variable_for_create(afd_client, event_variable):
    event_variable_name = util.extract_name_from_arn(event_variable.Arn)
    get_variables_worked, _ = validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable_name)
    if not get_variables_worked:
        raise exceptions.NotFound("event_variable", event_variable.Arn)


def _validate_inline_event_variable_for_create(afd_client, event_variable):
    if event_variable.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline event variables must include Name!")

    get_variables_worked, _ = validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable.Name)
    if get_variables_worked:
        raise exceptions.AlreadyExists("event_variable", event_variable.Name)

    common_helpers.create_inline_event_variable(frauddetector_client=afd_client, event_variable=event_variable)


def _validate_entity_types_for_create(afd_client, event_type_model: models.EventType):
    for entity_type in event_type_model.EntityTypes:
        _validate_entity_type_for_create(afd_client, entity_type)


def _validate_entity_type_for_create(afd_client, entity_type):
    if entity_type.Inline:
        _validate_inline_entity_type_for_create(afd_client, entity_type)
    else:
        _validate_referenced_entity_type_for_create(afd_client, entity_type)


def _validate_referenced_entity_type_for_create(afd_client, entity_type):
    entity_type_name = util.extract_name_from_arn(entity_type.Arn)
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type_name)
    if not get_entity_types_worked:
        raise exceptions.NotFound("entity_type", entity_type.Arn)


def _validate_inline_entity_type_for_create(afd_client, entity_type):
    if entity_type.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline entity types must include Name!")

    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type.Name)
    if get_entity_types_worked:
        raise exceptions.AlreadyExists("entity_type", entity_type.Name)

    common_helpers.put_inline_entity_type(afd_client, entity_type)


def _validate_labels_for_create(afd_client, event_type_model: models.EventType):
    for label in event_type_model.Labels:
        _validate_label_for_create(afd_client, label)


def _validate_label_for_create(afd_client, label):
    if label.Inline:
        _validate_inline_label_for_create(afd_client, label)
    else:
        _validate_referenced_label_for_create(afd_client, label)


def _validate_referenced_label_for_create(afd_client, label):
    label_name = util.extract_name_from_arn(label.Arn)
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label_name)
    if not get_labels_worked:
        raise exceptions.NotFound("label", label.Arn)


def _validate_inline_label_for_create(afd_client, label):
    if label.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline labels must include Name!")

    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label.Name)
    if get_labels_worked:
        raise exceptions.AlreadyExists("label", label.Name)

    common_helpers.put_inline_label(afd_client, label)
