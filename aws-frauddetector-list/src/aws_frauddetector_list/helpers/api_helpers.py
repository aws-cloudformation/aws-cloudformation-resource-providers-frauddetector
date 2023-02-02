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
