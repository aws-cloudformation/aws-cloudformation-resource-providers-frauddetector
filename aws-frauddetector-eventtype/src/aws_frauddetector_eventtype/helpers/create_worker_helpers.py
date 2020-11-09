import logging
from cloudformation_cli_python_lib import (
    exceptions,
)

from . import validation_helpers, common_helpers, util
from ..models import ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_dependencies_for_create(afd_client, model: ResourceModel):
    _validate_event_variables_for_create(afd_client, model)
    _validate_entity_types_for_create(afd_client, model)
    _validate_labels_for_create(afd_client, model)


def _validate_event_variables_for_create(afd_client, model: ResourceModel):
    for event_variable in model.EventVariables:
        _validate_event_variable_for_create(afd_client, event_variable)


def _validate_event_variable_for_create(afd_client, event_variable):
    # either support referenced variable via Arn, or inline variable w/ Name
    is_referenced_variable = not event_variable.Inline
    if is_referenced_variable:
        _validate_referenced_event_variable_for_create(afd_client, event_variable)
    else:
        _validate_inline_event_variable_for_create(afd_client, event_variable)


def _validate_referenced_event_variable_for_create(afd_client, event_variable):
    # throw not found exception if referenced variable does not exist
    event_variable_name = util.extract_name_from_arn(event_variable.Arn)
    # event_variable.Name = event_variable_name
    get_variables_worked, _ = \
        validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable_name)
    if not get_variables_worked:
        raise exceptions.NotFound('event_variable', event_variable.Arn)


def _validate_inline_event_variable_for_create(afd_client, event_variable):
    if event_variable.Name is None:
        raise exceptions.InvalidRequest('Error occurred: inline event variables must include Name!')

    # throw exception if inline variable already exists
    get_variables_worked, _ = \
        validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable.Name)
    if get_variables_worked:
        raise exceptions.AlreadyExists('event_variable', event_variable.Name)

    # create inline variable
    common_helpers.create_inline_event_variable(frauddetector_client=afd_client, event_variable=event_variable)


def _validate_entity_types_for_create(afd_client, model: ResourceModel):
    for entity_type in model.EntityTypes:
        _validate_entity_type_for_create(afd_client, entity_type)


def _validate_entity_type_for_create(afd_client, entity_type):
    # either support referenced entity_type via Arn, or inline entity_type w/ Name
    is_referenced_entity = not entity_type.Inline
    if is_referenced_entity:
        _validate_referenced_entity_type_for_create(afd_client, entity_type)
    else:
        _validate_inline_entity_type_for_create(afd_client, entity_type)


def _validate_referenced_entity_type_for_create(afd_client, entity_type):
    # throw not found exception if reference entity type does not exist
    entity_type_name = util.extract_name_from_arn(entity_type.Arn)
    # entity_type.Name = entity_type_name
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type_name)
    if not get_entity_types_worked:
        raise exceptions.NotFound('entity_type', entity_type.Arn)


def _validate_inline_entity_type_for_create(afd_client, entity_type):
    if entity_type.Name is None:
        raise exceptions.InvalidRequest('Error occurred: inline entity types must include Name!')

    # throw exception if inline entity type already exists
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type.Name)
    if get_entity_types_worked:
        raise exceptions.AlreadyExists('entity_type', entity_type.Name)

    # create inline entity type
    common_helpers.put_inline_entity_type(afd_client, entity_type)


def _validate_labels_for_create(afd_client, model: ResourceModel):
    for label in model.Labels:
        _validate_label_for_create(afd_client, label)


def _validate_label_for_create(afd_client, label):
    # either support referenced label via Arn, or inline label w/ Name
    is_referenced_entity = not label.Inline
    if is_referenced_entity:
        _validate_referenced_label_for_create(afd_client, label)
    else:
        _validate_inline_label_for_create(afd_client, label)


def _validate_referenced_label_for_create(afd_client, label):
    # throw not found exception if reference entity type does not exist
    label_name = util.extract_name_from_arn(label.Arn)
    # label.Name = label_name
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label_name)
    if not get_labels_worked:
        raise exceptions.NotFound('label', label.Arn)


def _validate_inline_label_for_create(afd_client, label):
    if label.Name is None:
        raise exceptions.InvalidRequest('Error occurred: inline labels must include Name!')

    # throw exception if inline entity type already exists
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label.Name)
    if get_labels_worked:
        raise exceptions.AlreadyExists('label', label.Name)

    # create inline label
    common_helpers.put_inline_label(afd_client, label)
