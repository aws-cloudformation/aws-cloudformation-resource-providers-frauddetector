import logging
from typing import List, Tuple, Dict, Optional, Sequence
from cloudformation_cli_python_lib import (
    exceptions,
)

import botocore
from . import api_helpers, util
from ..models import EventVariable

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def remove_none_arguments(args):
    LOG.debug(f"received arguments {args} to remove None from")
    if type(args) is str or args is None:
        LOG.debug("Args is string or none. returning args")
        return args
    new_args = {}
    LOG.debug(f"Checking args items for args: {args}")
    for key, value in args.items():
        LOG.debug(f"arg item key: {key}, value: {value}")
        if type(value) is dict:
            new_value = remove_none_arguments(value)
        elif type(value) is list:
            new_value = [remove_none_arguments(item) for item in value]
        else:
            new_value = value
        if new_value is not None:
            new_args[key] = new_value
    args = new_args
    LOG.debug(f"returning new args: {args}")
    return args


def check_if_get_variables_succeeds(frauddetector_client, variable_name):
    """
    This calls get_variables and returns True if it worked, along with the API response (True, response)
    If the call to get_variables fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param variable_name:  the name of the variable you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_variables_response = api_helpers.call_get_variables(frauddetector_client, variable_name)
        return True, get_variables_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting variable {variable_name}: {RNF}")
        return False, None


def check_batch_get_variable_errors(frauddetector_client, variable_names: List[str]) -> Tuple[bool, Dict[str, list]]:
    """
    Call batch_get_variable for all of the variable names supplied.
    If the call succeeds, return (True, response).
    If the call does not succeed, return (False, {}).
    """
    try:
        response = api_helpers.call_batch_get_variable(frauddetector_client=frauddetector_client, names=variable_names)
        return True, response
    except botocore.exceptions.ClientError as client_error:
        LOG.warning(f"Error calling batch get variable: {client_error}")
        return False, {}


def check_if_get_entity_types_succeeds(frauddetector_client, entity_type_name):
    """
    This calls get_entity_types and returns True if it worked, along with the API response (True, response)
    If the call to get_entity_types fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param entity_type_name:  the name of the entity_type you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_entity_types_response = api_helpers.call_get_entity_types(frauddetector_client, entity_type_name)
        return True, get_entity_types_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting entity_type {entity_type_name}: {RNF}")
        return False, None


def check_if_get_event_types_succeeds(frauddetector_client, event_type_to_check: str):
    """
    This calls get_event_types and returns True if the response contains an event type: (True, event_type)
    If the call does not return any event types, return (False, None)
    :param frauddetector_client: frauddetector boto3 client
    :param event_type_to_check: the name of the event type to check for
    :return: a tuple: (bool, returned_event_type)
    """
    try:
        get_event_types_response = api_helpers.call_get_event_types(frauddetector_client, event_type_to_check)
        return True, get_event_types_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting event type {event_type_to_check}: {RNF}")
        return False, None


def check_if_get_labels_succeeds(frauddetector_client, label_name):
    """
    This calls get_labels and returns True if it worked, along with the API response (True, response)
    If the call to get_labels fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param label_name:  the name of the label you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name)
        return True, get_labels_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting label {label_name}: {RNF}")
        return False, None


def check_batch_get_variables_for_event_variables(afd_client, variable_names: list) -> dict:
    success, response = check_batch_get_variable_errors(frauddetector_client=afd_client, variable_names=variable_names)
    if not success:
        LOG.warning("BatchGetVariable returned an unexpected failure, unable to complete CFN changeset execution.")
        raise exceptions.InternalFailure("Error occurred while getting variables, please try again later.")
    return response


def check_variable_differences(existing_event_variable, desired_event_variable):
    return {
        "defaultValue": existing_event_variable.DefaultValue != desired_event_variable.DefaultValue,
        "description": existing_event_variable.Description != desired_event_variable.Description,
        "variableType": existing_event_variable.VariableType != desired_event_variable.VariableType,
        "dataType": existing_event_variable.DataType != desired_event_variable.DataType,
        "dataSource": existing_event_variable.DataSource != desired_event_variable.DataSource,
        "tags": existing_event_variable.Tags != desired_event_variable.Tags,
    }


def check_variable_entries_are_valid(arguments_to_check: dict):
    variable_entries_to_check = arguments_to_check.get("variableEntries", [])
    required_attributes = {"dataSource", "dataType", "defaultValue", "name"}
    all_attributes = {
        "dataSource",
        "dataType",
        "defaultValue",
        "description",
        "name",
        "variableType",
    }
    for variable_entry in variable_entries_to_check:
        variable_attributes = set(variable_entry.keys())
        if not required_attributes.issubset(variable_attributes):
            missing_attributes = required_attributes.difference(variable_attributes)
            missing_attributes_message = (
                f"Variable Entries did not have the following required attributes: {missing_attributes}"
            )
            LOG.warning(missing_attributes_message)
            raise exceptions.InvalidRequest(missing_attributes_message)
        if not variable_attributes.issubset(all_attributes):
            unrecognized_attributes = variable_attributes.difference(all_attributes)
            unrecognized_attributes_message = (
                f"Error: variable entries has unrecognized attributes: {unrecognized_attributes}"
            )
            LOG.warning(unrecognized_attributes_message)
            raise exceptions.InvalidRequest(unrecognized_attributes_message)
    return True


def validate_event_variables_attributes(
    event_variables: Optional[Sequence[EventVariable]],
) -> Tuple[Dict[str, EventVariable], List[str]]:
    variables_by_name: Dict[str, EventVariable] = {}
    variable_names: List[str] = []
    for event_variable in event_variables:
        if event_variable.Inline:
            if event_variable.Name is None:
                raise exceptions.InvalidRequest("Error occurred: inline event variables must include Name!")
            variable_name = event_variable.Name
        else:
            if event_variable.Arn is None:
                raise exceptions.InvalidRequest("Error occurred: non-inline event variables must include Arn!")
            variable_name = util.extract_name_from_arn(event_variable.Arn)
        variables_by_name[variable_name] = event_variable
        variable_names.append(variable_name)
    return variables_by_name, variable_names


def validate_missing_variables_for_create(
    batch_get_variable_errors: list, variables_by_name: Dict[str, EventVariable]
) -> List[EventVariable]:
    inline_variables_to_create: List[EventVariable] = []
    for error in batch_get_variable_errors:
        errored_variable_name = error.get("name", None)
        modeled_variable = variables_by_name.pop(errored_variable_name, None)
        if not modeled_variable.Inline:
            raise exceptions.NotFound("event_variable", modeled_variable.Arn)
        inline_variables_to_create.append(modeled_variable)
    return inline_variables_to_create


def validate_all_event_variables_have_been_validated(unvalidated_variables: dict):
    if len(unvalidated_variables) != 0:
        LOG.error(
            "validate_dependencies_for_create did not validate all event variables! "
            "This is a bug in AFD's CFN Implementation!"
        )
        raise exceptions.InternalFailure("Error occurred while validating event variables, please try again later.")
