from typing import List
from . import validation_helpers

import functools
import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

# Maximum number of pages to get for paginated calls
# for page size of 100, 100 pages is 10,000 resources, which is twice the largest default service limit
MAXIMUM_NUMBER_OF_PAGES = 100


# Wrapper/decorator


def api_call_with_debug_logs(func):
    """
    Add some logs to the decorated function
    """
    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        LOG.debug(f'Starting function {func.__name__!r} with args {args} and kwargs {kwargs}')
        value = func(*args, **kwargs)
        LOG.debug(f'Finished function {func.__name__!r}, returning {value}')
        return value
    return log_wrapper


def paginated_api_call(item_to_collect, criteria_to_keep=lambda x, y: True, max_pages=MAXIMUM_NUMBER_OF_PAGES):
    """
    For a method that calls a paginated API (returns an object w/ 'nextToken' key),
    decorate with @paginated_api_call to get an exhaustive list returned,
    stopping at the maximum number of pages
    :param item_to_collect: string representing the key of the object that should be accumulated
    :param criteria_to_keep: function to determine if items should be kept - item_list, item -> bool
    :param max_pages: maximum number of pages allowed
    :return: an exhaustive list, containing the accumulated items from all pages from the API call
    """
    def paginated_api_call_decorator(func):
        @functools.wraps(func)
        def api_call_wrapper(*args, **kwargs):
            collected_items = []
            response = func(*args, **kwargs)

            def collect_items_of_interest_from_current_response():
                for item_of_interest in response.get(item_to_collect, []):
                    if criteria_to_keep(collected_items, item_of_interest):
                        collected_items.append(item_of_interest)

            collect_items_of_interest_from_current_response()
            count = 1

            while 'nextToken' in response and count < max_pages:
                next_token = response['nextToken']
                response = func(*args, nextToken=next_token, **kwargs)
                collect_items_of_interest_from_current_response()
                count += 1

            response[item_to_collect] = collected_items
            return response
        return api_call_wrapper
    return paginated_api_call_decorator


# Put APIs


@api_call_with_debug_logs
def call_put_outcome(frauddetector_client,
                     outcome_name: str,
                     outcome_tags: List[dict] = None,
                     outcome_description: str = None):
    """
    Call put_outcome with the given frauddetector client and the given arguments.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome
    :param outcome_tags: tags to attach to the outcome (default is None)
    :param outcome_description: description of the outcome (default is None)
    :return: API response from frauddetector_client
    """
    args = {
        "name": outcome_name,
        "tags": outcome_tags,
        "description": outcome_description
    }
    args = validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_outcome(**args)


# Get APIs


@paginated_api_call(item_to_collect='outcomes')
@api_call_with_debug_logs
def call_get_outcomes(frauddetector_client, outcome_name: str = None):
    """
    Call get_outcomes with the given frauddetector client and the given arguments.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome to get (default is None)
    :return: get a single outcome if outcome_name is specified, otherwise get all outcomes
    """
    args = {
        "name": outcome_name
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_outcomes(**args)


# Delete APIs


@api_call_with_debug_logs
def call_delete_outcome(frauddetector_client, outcome_name: str):
    """
    Call delete_outcome for a given outcome name with the given frauddetector client.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome to delete
    :return: success will return a 200 with no body
    """
    return frauddetector_client.delete_outcome(name=outcome_name)


# Tagging


@paginated_api_call(item_to_collect='tags')
@api_call_with_debug_logs
def call_list_tags_for_resource(frauddetector_client, resource_arn: str):
    """
    Call list_tags_for_resource for a given ARN with the given frauddetector client.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to get tags for
    :return: result has an exhaustive list of tags attached to the resource
    """
    return frauddetector_client.list_tags_for_resource(resourceARN=resource_arn)


@api_call_with_debug_logs
def call_tag_resource(frauddetector_client, resource_arn: str, tags: List[dict]):
    """
    Call tag_resource with the given frauddetector client and parameters.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to attach tags to
    :param tags: tags to attach to the resource, as a list of dicts [{'key': '...', 'value': '...'}]
    :return: success will return a 200 with no body
    """
    return frauddetector_client.tag_resource(resourceARN=resource_arn, tags=tags)


@api_call_with_debug_logs
def call_untag_resource(frauddetector_client, resource_arn: str, tag_keys: List[str]):
    """
    Call untag_resource with the given frauddetector client and parameters.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to remove tags from
    :param tag_keys: tags to attach to the resource, as a list of str ['key1', 'key2']
    :return: success will return a 200 with no body
    """
    return frauddetector_client.untag_resource(resourceARN=resource_arn, tagKeys=tag_keys)
