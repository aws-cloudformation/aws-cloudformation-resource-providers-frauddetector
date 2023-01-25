from typing import List
from . import validation_helpers

import functools
import logging
import time

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(level=logging.DEBUG)

# Maximum number of pages to get for paginated calls
# for page size of 100, 100 pages is 10,000 resources, which is twice the largest default service limit
MAXIMUM_NUMBER_OF_PAGES = 100

# Number of seconds to wait for eventually consistency for `retry_not_found_exceptions` decorator
CONSISTENCY_SLEEP_TIME = 1.0

LIST_UPDATE_REPLACE = "REPLACE"

# Wrapper/decorator


def api_call_with_debug_logs(func):
    """
    Add some logs to the decorated function
    """

    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        LOG.debug(f"Starting function {func.__name__!r} with args {args} and kwargs {kwargs}")
        value = func(*args, **kwargs)
        LOG.debug(f"Finished function {func.__name__!r}, returning {value}")
        return value

    return log_wrapper


def retry_not_found_exceptions(func):
    """
    Retries boto3 not found exception for the decorated function.
    """

    @functools.wraps(func)
    def retry_not_found_exceptions_wrapper(*args, **kwargs):
        afd_client = kwargs.get("frauddetector_client", None)
        if not afd_client:
            if len(args) > 0:
                afd_client = args[0]
            else:
                # We can't grab afd_client, so we can't compare to AFD's RNF Exception.
                # Just run the function, rather than throwing an error
                LOG.error(
                    "retry_not_found_exceptions_wrapper could not find the afd client! "
                    "Perhaps the decorator was added to a method that is not supported?"
                )
                return func(*args, **kwargs)
        try:
            return func(*args, **kwargs)
        except afd_client.exceptions.ResourceNotFoundException:
            LOG.warning(
                f"caught a resource not found exception."
                f" sleeping {CONSISTENCY_SLEEP_TIME} seconds and retrying api call for consistency..."
            )
            time.sleep(CONSISTENCY_SLEEP_TIME)
            return func(*args, **kwargs)

    return retry_not_found_exceptions_wrapper


def paginated_api_call(
    item_to_collect,
    criteria_to_keep=lambda x, y: True,
    max_pages=MAXIMUM_NUMBER_OF_PAGES,
):
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

            while "nextToken" in response and count < max_pages:
                next_token = response["nextToken"]
                response = func(*args, nextToken=next_token, **kwargs)
                collect_items_of_interest_from_current_response()
                count += 1

            response[item_to_collect] = collected_items
            return response

        return api_call_wrapper

    return paginated_api_call_decorator


# Create APIs


@api_call_with_debug_logs
def call_create_list(
    frauddetector_client,
    list_name: str,
    list_variable_type: str,
    list_description: str,
    list_elements: List[str],
    list_tags: List[dict] = None,
):
    args = {
        "name": list_name,
        "elements": list(list_elements),
        "variableType": list_variable_type,
        "description": list_description,
        "tags": list_tags,
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.create_list(**args)


# Update APIs


@retry_not_found_exceptions
@api_call_with_debug_logs
def call_update_list(
    frauddetector_client,
    list_name: str,
    list_variable_type: str,
    list_description: str,
    list_elements: List[str] = {},
    list_tags: List[dict] = None,
):
    args = {
        "name": list_name,
        "elements": list(list_elements),
        "variableType": list_variable_type,
        "description": list_description,
        "tags": list_tags,
        "updateMode": LIST_UPDATE_REPLACE,
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.update_list(**args)


# Get APIs


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="lists")
@api_call_with_debug_logs
def call_get_lists_metadata(frauddetector_client, list_name: str = None):
    args = {"name": list_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_lists_metadata(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="elements")
@api_call_with_debug_logs
def call_get_list_elements(frauddetector_client, list_name: str):
    args = {"name": list_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_list_elements(**args)


# Delete APIs


@api_call_with_debug_logs
def call_delete_list(frauddetector_client, list_name: str):
    return frauddetector_client.delete_list(name=list_name)


# Tagging
@retry_not_found_exceptions
@paginated_api_call(item_to_collect="tags")
@api_call_with_debug_logs
def call_list_tags_for_resource(frauddetector_client, resource_arn: str):
    """
    Call list_tags_for_resource for a given ARN with the given frauddetector client.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to get tags for
    :return: result has an exhaustive list of tags attached to the resource
    """
    return frauddetector_client.list_tags_for_resource(resourceARN=resource_arn)


@retry_not_found_exceptions
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


@retry_not_found_exceptions
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
