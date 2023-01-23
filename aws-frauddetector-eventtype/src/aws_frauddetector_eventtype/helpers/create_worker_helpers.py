import logging
from cloudformation_cli_python_lib import (
    exceptions,
)
from typing import Dict, List

from . import validation_helpers, common_helpers, util
from ..models import ResourceModel, EventVariable

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_dependencies_for_create(afd_client, model: ResourceModel):
    inline_vars_to_create: List[EventVariable] = _validate_event_variables_for_create(afd_client, model)
    common_helpers.create_inline_event_variables(frauddetector_client=afd_client, event_variables=inline_vars_to_create)

    _validate_entity_types_for_create(afd_client, model)
    _validate_labels_for_create(afd_client, model)


def _validate_event_variables_for_create(afd_client, model: ResourceModel) -> List[EventVariable]:
    variables_by_name, variable_names = validation_helpers.validate_event_variables_attributes(model.EventVariables)
    response = validation_helpers.check_batch_get_variables_for_event_variables(afd_client, variable_names)
    inline_variables_to_create = validation_helpers.validate_missing_variables_for_create(
        response.get("errors", []), variables_by_name
    )
    _validate_existing_variables_for_create(response.get("variables", []), variables_by_name)
    validation_helpers.validate_all_event_variables_have_been_validated(variables_by_name)
    # Return a list of event variables that need to be created inline
    return inline_variables_to_create


def _validate_existing_variables_for_create(batch_get_variable_variables: list, variables_by_name: dict):
    for variable in batch_get_variable_variables:
        succeeded_variable_name = variable.get("name", None)
        modeled_variable = variables_by_name.pop(succeeded_variable_name, None)
        if modeled_variable.Inline:
            raise exceptions.AlreadyExists("event_variable", modeled_variable.Name)


def _validate_entity_types_for_create(afd_client, model: ResourceModel):
    for entity_type in model.EntityTypes:
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


def _validate_labels_for_create(afd_client, model: ResourceModel):
    for label in model.Labels:
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
