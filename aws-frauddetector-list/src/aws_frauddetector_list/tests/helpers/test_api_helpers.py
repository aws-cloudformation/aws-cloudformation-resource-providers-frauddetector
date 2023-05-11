from ...helpers import api_helpers, validation_helpers  # for assertion
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


def test_get_calls(monkeypatch):
    required_arguments = [
        {
            "api_helper_call_func": api_helpers.call_get_lists_metadata,
            "api_name": "get_lists_metadata",
            "args": {},
        },
    ]
    for api_call_to_test in required_arguments:
        current_args = api_call_to_test.get("args", {})
        should_check_validation_helper = current_args.get("should_check_validation_helper", True)
        if "should_check_validation_helper" in current_args:
            del current_args["should_check_validation_helper"]
        _test_api_helper_call(
            monkeypatch=monkeypatch,
            should_check_validation_helper=should_check_validation_helper,
            **api_call_to_test,
        )


def test_delete_calls(monkeypatch):
    required_arguments = [
        {
            "api_helper_call_func": api_helpers.call_delete_list,
            "api_name": "delete_list",
            "args": {
                "list_name": unit_test_utils.FAKE_EVENT_TYPE.get("name"),
                "should_check_validation_helper": False,
            },
        },
    ]
    for api_call_to_test in required_arguments:
        current_args = api_call_to_test.get("args", {})
        should_check_validation_helper = current_args.get("should_check_validation_helper", True)
        if "should_check_validation_helper" in current_args:
            del current_args["should_check_validation_helper"]
        _test_api_helper_call(
            monkeypatch=monkeypatch,
            should_check_validation_helper=should_check_validation_helper,
            **api_call_to_test,
        )


def test_create_calls(monkeypatch):
    required_arguments = [
        {
            "api_helper_call_func": api_helpers.call_create_list,
            "api_name": "create_list",
            "args": {
                "list_name": unit_test_utils.FAKE_LIST.get("name"),
                "list_variable_type": unit_test_utils.FAKE_LIST.get("variableType"),
                "list_description": unit_test_utils.FAKE_LIST.get("description"),
                "list_elements": unit_test_utils.FAKE_LIST.get("elements"),
            },
        }
    ]
    for api_call_to_test in required_arguments:
        _test_api_helper_call(monkeypatch=monkeypatch, **api_call_to_test)


def test_update_calls(monkeypatch):
    required_arguments = [
        {
            "api_helper_call_func": api_helpers.call_update_list,
            "api_name": "update_list",
            "args": {
                "list_description": unit_test_utils.FAKE_LIST.get("description"),
                "list_elements": unit_test_utils.FAKE_LIST.get("elements"),
                "list_variable_type": unit_test_utils.FAKE_LIST.get("variableType"),
                "list_name": unit_test_utils.FAKE_LIST.get("name"),
            },
        },
    ]
    for api_call_to_test in required_arguments:
        _test_api_helper_call(monkeypatch=monkeypatch, **api_call_to_test)


def _test_api_helper_call(
    monkeypatch,
    api_helper_call_func,
    api_name,
    args,
    should_check_validation_helper=True,
):
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_api_call = MagicMock(return_value={})
    mock_remove_none_arguments = MagicMock(return_value={})
    monkeypatch.setattr(mock_afd_client, api_name, mock_api_call)
    monkeypatch.setattr(validation_helpers, "remove_none_arguments", mock_remove_none_arguments)

    # Act
    api_helper_call_func(mock_afd_client, **args)

    # Assert
    if should_check_validation_helper:
        mock_remove_none_arguments.assert_called_once()
    mock_api_call.assert_called_once()
