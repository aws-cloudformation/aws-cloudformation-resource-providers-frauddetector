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


def check_if_get_outcomes_succeeds(frauddetector_client, outcome_name):
    """
    This calls get_outcomes and returns True if it worked, along with the API response (True, response)
    If the call to get_outcomes fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param outcome_name:  the name of the outcome you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_outcomes_response = api_helpers.call_get_outcomes(frauddetector_client, outcome_name)
        return True, get_outcomes_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting outcome {outcome_name}: {RNF}")
        return False, None
