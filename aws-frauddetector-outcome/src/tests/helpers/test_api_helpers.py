from aws_frauddetector_outcome.helpers import api_helpers
from .. import unit_test_utils
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

NUMBER_OF_ITEMS_PER_PAGE = 2
MAX_PAGES = 10


def test_retry_not_found_exceptions_decorator_happy_case():
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    mock_afd_client.get_labels.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_labels"),
        {"labels": [{"property": f"{j}"} for j in range(NUMBER_OF_ITEMS_PER_PAGE)]},
    ]

    @api_helpers.retry_not_found_exceptions
    def call_get_labels(frauddetector_client):
        return frauddetector_client.get_labels()

    response = call_get_labels(mock_afd_client)
    assert len(response["labels"]) == NUMBER_OF_ITEMS_PER_PAGE
    assert mock_afd_client.get_labels.call_count == 2


def test_retry_not_found_exceptions_decorator_no_exception():
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock(
        return_value={"labels": [{"property": f"{j}"} for j in range(NUMBER_OF_ITEMS_PER_PAGE)]}
    )

    @api_helpers.retry_not_found_exceptions
    def call_get_labels(frauddetector_client):
        return frauddetector_client.get_labels()

    response = call_get_labels(mock_afd_client)
    assert len(response["labels"]) == NUMBER_OF_ITEMS_PER_PAGE
    assert mock_afd_client.get_labels.call_count == 1


def test_retry_not_found_exceptions_decorator_multi_page():
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    side_effects = [ClientError({"Code": "", "Message": ""}, "get_labels")]
    side_effects.extend(
        [
            {
                "nextToken": "notNone",
                "labels": [{"property": f"{i}.{j}"} for j in range(NUMBER_OF_ITEMS_PER_PAGE)],
            }
            for i in range(MAX_PAGES + 10)
        ]
    )
    mock_afd_client.get_labels.side_effect = side_effects

    @api_helpers.retry_not_found_exceptions
    @api_helpers.paginated_api_call("labels", max_pages=MAX_PAGES)
    @api_helpers.api_call_with_debug_logs
    def call_get_labels(frauddetector_client, nextToken=None):
        return frauddetector_client.get_labels(nextToken)

    response = call_get_labels(mock_afd_client)
    assert len(response["labels"]) == NUMBER_OF_ITEMS_PER_PAGE * MAX_PAGES
    assert mock_afd_client.get_labels.call_count == MAX_PAGES + 1


def test_paginated_api_call_not_infinite_loop():
    test_fn = MagicMock()
    test_fn.side_effect = [
        {
            "nextToken": "notNone",
            "someThings": [{"ruleVersion": f"{i}.{j}"} for j in range(NUMBER_OF_ITEMS_PER_PAGE)],
        }
        for i in range(MAX_PAGES + 10)
    ]

    @api_helpers.api_call_with_debug_logs
    @api_helpers.paginated_api_call("someThings", max_pages=MAX_PAGES)
    def call_test_fn(nextToken=None):
        return test_fn(nextToken)

    response = call_test_fn()
    assert len(response["someThings"]) == NUMBER_OF_ITEMS_PER_PAGE * MAX_PAGES
    assert test_fn.call_count == MAX_PAGES


def test_paginated_api_call_matches_criteria():
    test_fn = MagicMock()
    test_fn.side_effect = [
        {
            "nextToken": "notNone",
            "someThings": [{"someAttribute": f"{i}"} for i in range(NUMBER_OF_ITEMS_PER_PAGE)],
        }
        for _ in range(MAX_PAGES)
    ]

    # only keep items if someAttribute is '0'
    def criteria(_, item):
        return item.get("someAttribute", "") == "0"

    @api_helpers.api_call_with_debug_logs
    @api_helpers.paginated_api_call("someThings", criteria_to_keep=criteria, max_pages=MAX_PAGES)
    def call_test_fn(nextToken=None):
        return test_fn(nextToken)

    response = call_test_fn()

    # The criteria is for someAttribute = 0, so only one 'someThing' per page meets the criteria
    assert len(response["someThings"]) == MAX_PAGES
    assert test_fn.call_count == MAX_PAGES
