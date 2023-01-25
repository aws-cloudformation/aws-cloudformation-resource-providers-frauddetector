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


def check_if_get_lists_metadata_succeeds(frauddetector_client, list_name):
    """
    This calls get_lists_metadata and returns True if it worked, along with the API response (True, response)
    If the call to get_labels fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param label_name:  the name of the label you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_lists_metadata_response = api_helpers.call_get_lists_metadata(frauddetector_client, list_name)
        return True, get_lists_metadata_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting list {list_name}: {RNF}")
        return False, None
