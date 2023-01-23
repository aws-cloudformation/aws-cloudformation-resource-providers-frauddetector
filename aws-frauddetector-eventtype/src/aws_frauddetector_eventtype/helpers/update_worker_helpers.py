import logging
from cloudformation_cli_python_lib import (
    exceptions,
)
from typing import List, Tuple, Dict, Optional, Sequence, Set

from . import validation_helpers, api_helpers, common_helpers, util
from ..models import ResourceModel, EventVariable

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_dependencies_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    # Validate changes and get changes to make to inline resources
    inline_vars_to_create, inline_vars_to_update = _validate_event_variables_for_update(
        afd_client, model, previous_model
    )
    # TODO: delay creation of inline entity types and labels until validation is complete
    _validate_entity_types_for_update(afd_client, model, previous_model)
    _validate_labels_for_update(afd_client, model, previous_model)

    # Create and Update inline resources as necessary
    common_helpers.create_inline_event_variables(frauddetector_client=afd_client, event_variables=inline_vars_to_create)
    _update_inline_event_variables_for_update(frauddetector_client=afd_client, event_variables=inline_vars_to_update)

    # TODO: return changes to inline resources for rollback when put event type fails


def _validate_event_variables_for_update(
    afd_client, model: ResourceModel, previous_model: ResourceModel
) -> Tuple[List[EventVariable], List[EventVariable]]:
    # Validate event variable model changes.
    # As it stands today, event variables cannot be removed from an event type, but they can be added or changed.
    new_variables_by_name, new_variable_names = validation_helpers.validate_event_variables_attributes(
        model.EventVariables
    )
    changed_variable_names = _validate_event_variable_model_changes_for_update(
        previous_model.EventVariables, new_variables_by_name
    )

    # Call BatchGetVariables to check state for event variables.
    response = validation_helpers.check_batch_get_variables_for_event_variables(afd_client, new_variable_names)

    # Validate event variable changes against the state of the system.
    inline_variables_to_create = validation_helpers.validate_missing_variables_for_create(
        response.get("errors", []), new_variables_by_name
    )
    inline_variables_to_update = _validate_existing_variables_for_update(
        response.get("variables", []), new_variables_by_name, changed_variable_names
    )
    validation_helpers.validate_all_event_variables_have_been_validated(new_variables_by_name)

    # Return inline variables to create and update
    return inline_variables_to_create, inline_variables_to_update


def _validate_event_variable_model_changes_for_update(
    previous_variables: Optional[Sequence[EventVariable]], new_variables_by_name: Dict[str, EventVariable]
) -> Set[str]:
    variable_names_with_model_changes = set()
    for previous_variable in previous_variables:
        # Get variable name from previous variable model
        if previous_variable.Inline:
            variable_name = previous_variable.Name
        else:
            variable_name = util.extract_name_from_arn(previous_variable.Arn)

        # Validate event variables aren't removed.
        if variable_name not in new_variables_by_name:
            raise exceptions.InvalidRequest(
                f"Error: cannot remove event variables! Event variable {variable_name} was removed."
            )
        new_variable = new_variables_by_name.get(variable_name)

        # Validate variable is not switched from referenced to inline.
        # Variables can be switched from inline to referenced (not inline), but not vice versa.
        # It cannot be determined if referenced variables are managed by a separate CloudFormation stack.
        if not previous_variable.Inline and new_variable.Inline:
            raise exceptions.InvalidRequest(
                f"Error: cannot update referenced event variable {variable_name} to be inline! "
                "Event variables can be updated from inline to referenced, but not vice versa."
            )

        # Validate event variables don't have any other invalid changes.
        differences = validation_helpers.check_variable_differences(previous_variable, new_variable)
        if differences["dataSource"] or differences["dataType"]:
            raise exceptions.InvalidRequest(
                "Error occurred: cannot update event variable data source or data type! "
                f"Event variable {variable_name} changed data source or data type."
            )
        if differences["variableType"] and previous_variable.VariableType is not None:
            raise exceptions.InvalidRequest(
                "Error occurred: cannot update event variable variable-type! "
                f"Event variable {variable_name} changed variable-type."
            )
        total_number_of_changes = sum([is_different for attribute, is_different in differences.items()])
        if total_number_of_changes > 0:
            variable_names_with_model_changes.add(variable_name)
    return variable_names_with_model_changes


def _validate_existing_variables_for_update(
    batch_get_variable_variables: list, variables_by_name: Dict[str, EventVariable], changed_variable_names: Set[str]
) -> List[EventVariable]:
    inline_variables_to_update: List[EventVariable] = []
    for existing_variable in batch_get_variable_variables:
        variable_name = existing_variable.get("name", None)
        modeled_variable = variables_by_name.pop(variable_name, None)
        if not modeled_variable.Inline or variable_name not in changed_variable_names:
            continue
        # Arn is readonly property, so it will not be attached to input model for inline event variable.
        modeled_variable.Arn = existing_variable.get("arn", None)
        inline_variables_to_update.append(modeled_variable)
    return inline_variables_to_update


def _update_inline_event_variables_for_update(frauddetector_client, event_variables: List[EventVariable]) -> None:
    for event_variable in event_variables:
        if event_variable.Tags:
            common_helpers.update_tags(
                frauddetector_client=frauddetector_client,
                afd_resource_arn=event_variable.Arn,
                new_tags=list(event_variable.Tags),
            )
        api_helpers.call_update_variable(
            variable_name=event_variable.Name,
            frauddetector_client=frauddetector_client,
            variable_default_value=event_variable.DefaultValue,
            variable_description=event_variable.Description,
            variable_type=event_variable.VariableType,
        )


def _validate_entity_types_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    previous_entity_types = {entity_type.Name: entity_type for entity_type in previous_model.EntityTypes}
    new_entity_type_names = set()
    for entity_type in model.EntityTypes:
        _validate_entity_type_for_update(afd_client, entity_type, previous_entity_types)
        new_entity_type_names.add(entity_type.Name)

    # remove previous inline entity types that are no longer in the event type
    for (
        previous_entity_type_name,
        previous_entity_type,
    ) in previous_entity_types.items():
        if previous_entity_type_name not in new_entity_type_names and previous_entity_type.Inline:
            api_helpers.call_delete_entity_type(
                frauddetector_client=afd_client,
                entity_type_name=previous_entity_type_name,
            )


def _validate_entity_type_for_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Inline:
        _validate_inline_entity_type_for_update(afd_client, entity_type, previous_entity_types)
    else:
        _validate_referenced_entity_type_for_update(afd_client, entity_type)


def _validate_referenced_entity_type_for_update(afd_client, entity_type):
    entity_type_name = util.extract_name_from_arn(entity_type.Arn)
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type_name)
    if not get_entity_types_worked:
        raise exceptions.NotFound("entity_type", entity_type.Arn)


def _validate_inline_entity_type_for_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline entity types must include Name!")

    previous_entity_type = previous_entity_types.get(entity_type.Name, None)
    if not previous_entity_type:
        # put inline entity type that does not already exist
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
    else:
        # get existing entity type to get arn. Arn is readonly property, so it will not be attached to input model
        (
            get_entity_types_worked,
            get_entity_types_response,
        ) = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type.Name)
        if not get_entity_types_worked:
            raise RuntimeError(f"Previously existing entity type {entity_type.Name} no longer exists!")
        entity_type.Arn = get_entity_types_response.get("entityTypes")[0].get("arn")
        # put existing inline entity type and update tags
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
        if hasattr(entity_type, "Tags"):
            common_helpers.update_tags(
                frauddetector_client=afd_client,
                afd_resource_arn=entity_type.Arn,
                new_tags=entity_type.Tags,
            )


def _validate_labels_for_update(afd_client, model: ResourceModel, previous_model: ResourceModel):
    previous_labels = {label.Name: label for label in previous_model.Labels}
    new_label_names = set()
    for label in model.Labels:
        _validate_label_for_update(afd_client, label, previous_labels)
        new_label_names.add(label.Name)

    # remove previous inline labels that are no longer in the event type
    # TODO: throw invalid request for this invalid update
    for previous_label_name, previous_label in previous_labels.items():
        if previous_label_name not in new_label_names and previous_label.Inline:
            api_helpers.call_delete_label(frauddetector_client=afd_client, label_name=previous_label_name)


def _validate_label_for_update(afd_client, label, previous_labels):
    if label.Inline:
        _validate_inline_label_for_update(afd_client, label, previous_labels)
    else:
        _validate_referenced_label_for_update(afd_client, label)


def _validate_referenced_label_for_update(afd_client, label):
    label_name = util.extract_name_from_arn(label.Arn)
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label_name)
    if not get_labels_worked:
        raise exceptions.NotFound("label", label.Arn)


def _validate_inline_label_for_update(afd_client, label, previous_labels):
    if label.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline labels must include Name!")

    previous_label = previous_labels.get(label.Name, None)
    if not previous_label:
        # put inline label that does not already exist
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
    else:
        # get existing label to get arn. Arn is readonly property, so it will not be attached to input model
        (
            get_labels_worked,
            get_labels_response,
        ) = validation_helpers.check_if_get_labels_succeeds(afd_client, label.Name)
        if not get_labels_worked:
            raise RuntimeError(f"Previously existing label {label.Name} no longer exists!")
        label.Arn = get_labels_response.get("labels")[0].get("arn")
        # put existing inline label and update tags
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
        if hasattr(label, "Tags"):
            common_helpers.update_tags(
                frauddetector_client=afd_client,
                afd_resource_arn=label.Arn,
                new_tags=label.Tags,
            )
