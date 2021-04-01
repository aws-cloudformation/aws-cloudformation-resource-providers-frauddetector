import logging
from cloudformation_cli_python_lib import (
    exceptions,
)

from . import validation_helpers, api_helpers, common_helpers, util
from ..models import ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_dependencies_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    # TODO: revisit  this validation when/if we support in-place teardown
    # is_teardown_required = _determine_if_teardown_is_required(afd_client, model, previous_model)
    # if is_teardown_required and not model.AllowTeardown:
    #     raise RuntimeError(TEARDOWN_CONFLICT_MESSAGE)
    _validate_event_variables_for_update(afd_client, model, previous_model)
    _validate_entity_types_for_update(afd_client, model, previous_model)
    _validate_labels_for_update(afd_client, model, previous_model)


def _validate_event_variables_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    previous_variables = {variable.Name: variable for variable in previous_model.EventVariables}
    new_event_variable_names = set()
    for event_variable in model.EventVariables:
        _validate_event_variable_for_update(afd_client, event_variable, previous_variables)
        new_event_variable_names.add(event_variable.Name)

    # remove previous inline variables that are no longer in the event type
    for previous_variable_name, previous_variable in previous_variables.items():
        if previous_variable_name not in new_event_variable_names and previous_variable.Inline:
            api_helpers.call_delete_variable(frauddetector_client=afd_client, variable_name=previous_variable_name)


def _validate_event_variable_for_update(afd_client, event_variable, previous_variables):
    if event_variable.Inline:
        _validate_inline_event_variable_for_update(afd_client, event_variable, previous_variables)
    else:
        _validate_referenced_event_variable_for_update(afd_client, event_variable)


def _validate_referenced_event_variable_for_update(afd_client, event_variable):
    event_variable_name = util.extract_name_from_arn(event_variable.Arn)
    get_variables_worked, _ = \
        validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable_name)
    if not get_variables_worked:
        raise exceptions.NotFound('event_variable', event_variable.Arn)


def _validate_inline_event_variable_for_update(afd_client, event_variable, previous_variables):
    if not event_variable.Name:
        raise exceptions.InvalidRequest('Error occurred: inline event variables must include Name!')

    # TODO: update this logic if we support in-place Teardown
    #       This difference would require teardown if we were to support it

    # check for differences in dataSource or dataType
    differences = {}
    previous_variable = previous_variables.get(event_variable.Name, None)
    if previous_variable:
        differences = validation_helpers.check_variable_differences(previous_variable, event_variable)
    if differences['dataSource'] or differences['dataType']:
        raise exceptions.InvalidRequest('Error occurred: cannot update event variable data source or data type!')

    if not previous_variable:
        # create inline variable that does not already exist
        common_helpers.create_inline_event_variable(frauddetector_client=afd_client, event_variable=event_variable)
    else:
        # get existing variable to get arn. Arn is readonly property, so it will not be attached to input model
        get_variables_worked, get_variables_response =\
            validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable.Name)
        if not get_variables_worked:
            raise RuntimeError(f"Previously existing event variable {event_variable.Name} no longer exists!")
        event_variable.Arn = get_variables_response.get('variables')[0].get('arn')
        # update existing inline variable
        if hasattr(event_variable, 'Tags'):
            common_helpers.update_tags(frauddetector_client=afd_client,
                                       afd_resource_arn=event_variable.Arn,
                                       new_tags=event_variable.Tags)
        var_type = [None, event_variable.VariableType][event_variable.VariableType != previous_variable.VariableType]
        api_helpers.call_update_variable(variable_name=event_variable.Name,
                                         frauddetector_client=afd_client,
                                         variable_default_value=event_variable.DefaultValue,
                                         variable_description=event_variable.Description,
                                         variable_type=var_type)


def _validate_entity_types_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    previous_entity_types = {entity_type.Name: entity_type for entity_type in previous_model.EntityTypes}
    new_entity_type_names = set()
    for entity_type in model.EntityTypes:
        _validate_entity_type_for_update(afd_client, entity_type, previous_entity_types)
        new_entity_type_names.add(entity_type.Name)

    # remove previous inline entity types that are no longer in the event type
    for previous_entity_type_name, previous_entity_type in previous_entity_types.items():
        if previous_entity_type_name not in new_entity_type_names and previous_entity_type.Inline:
            api_helpers.call_delete_entity_type(frauddetector_client=afd_client,
                                                entity_type_name=previous_entity_type_name)


def _validate_entity_type_for_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Inline:
        _validate_inline_entity_type_for_update(afd_client, entity_type, previous_entity_types)
    else:
        _validate_referenced_entity_type_for_update(afd_client, entity_type)


def _validate_referenced_entity_type_for_update(afd_client, entity_type):
    entity_type_name = util.extract_name_from_arn(entity_type.Arn)
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type_name)
    if not get_entity_types_worked:
        raise exceptions.NotFound('entity_type', entity_type.Arn)


def _validate_inline_entity_type_for_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Name is None:
        raise exceptions.InvalidRequest('Error occurred: inline entity types must include Name!')

    previous_entity_type = previous_entity_types.get(entity_type.Name, None)
    if not previous_entity_type:
        # put inline entity type that does not already exist
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
    else:
        # get existing entity type to get arn. Arn is readonly property, so it will not be attached to input model
        get_entity_types_worked, get_entity_types_response =\
            validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type.Name)
        if not get_entity_types_worked:
            raise RuntimeError(f"Previously existing entity type {entity_type.Name} no longer exists!")
        entity_type.Arn = get_entity_types_response.get('entityTypes')[0].get('arn')
        # put existing inline entity type and update tags
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
        if hasattr(entity_type, 'Tags'):
            common_helpers.update_tags(frauddetector_client=afd_client,
                                       afd_resource_arn=entity_type.Arn,
                                       new_tags=entity_type.Tags)


def _validate_labels_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    previous_labels = {label.Name: label for label in previous_model.Labels}
    new_label_names = set()
    for label in model.Labels:
        _validate_label_for_update(afd_client, label, previous_labels)
        new_label_names.add(label.Name)

    # remove previous inline labels that are no longer in the event type
    for previous_label_name, previous_label in previous_labels.items():
        if previous_label_name not in new_label_names and previous_label.Inline:
            api_helpers.call_delete_label(frauddetector_client=afd_client,
                                          label_name=previous_label_name)


def _validate_label_for_update(afd_client, label, previous_labels):
    if label.Inline:
        _validate_inline_label_for_update(afd_client, label, previous_labels)
    else:
        _validate_referenced_label_for_update(afd_client, label)


def _validate_referenced_label_for_update(afd_client, label):
    label_name = util.extract_name_from_arn(label.Arn)
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label_name)
    if not get_labels_worked:
        raise exceptions.NotFound('label', label.Arn)


def _validate_inline_label_for_update(afd_client, label, previous_labels):
    if label.Name is None:
        raise exceptions.InvalidRequest('Error occurred: inline labels must include Name!')

    previous_label = previous_labels.get(label.Name, None)
    if not previous_label:
        # put inline label that does not already exist
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
    else:
        # get existing label to get arn. Arn is readonly property, so it will not be attached to input model
        get_labels_worked, get_labels_response = validation_helpers.check_if_get_labels_succeeds(afd_client, label.Name)
        if not get_labels_worked:
            raise RuntimeError(f"Previously existing label {label.Name} no longer exists!")
        label.Arn = get_labels_response.get('labels')[0].get('arn')
        # put existing inline label and update tags
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
        if hasattr(label, 'Tags'):
            common_helpers.update_tags(frauddetector_client=afd_client,
                                       afd_resource_arn=label.Arn,
                                       new_tags=label.Tags)
