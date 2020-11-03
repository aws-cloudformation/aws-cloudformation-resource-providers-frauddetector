import logging

from . import api_helpers

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def remove_none_arguments(args):
    keys_to_remove = {key for key, value in args.items() if value is None}
    for key in keys_to_remove:
        del args[key]
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
        return False, None


def check_variable_differences(existing_event_variable, desired_event_variable):
    return {
        "defaultValue": existing_event_variable.DefaultValue != desired_event_variable.DefaultValue,
        "description": existing_event_variable.Description != desired_event_variable.Description,
        "variableType": existing_event_variable.VariableType != desired_event_variable.VariableType,
        "dataType": existing_event_variable.DataType != desired_event_variable.DataType,
        "tags": existing_event_variable.Tags != desired_event_variable.Tags
    }
