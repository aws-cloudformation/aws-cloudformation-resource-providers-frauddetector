import logging
from cloudformation_cli_python_lib import (
    exceptions,
)
from typing import List

from . import api_helpers

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def remove_none_arguments(args):
    keys_to_remove = {key for key, value in args.items() if value is None}
    for key in keys_to_remove:
        del args[key]
    return args


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
