from aws_frauddetector_outcome.helpers import api_helpers
from unittest.mock import MagicMock

NUMBER_OF_ITEMS_PER_PAGE = 2
MAX_PAGES = 10


def test_paginated_api_call_not_infinite_loop():
    test_fn = MagicMock()
    test_fn.side_effect = [
        {
            'nextToken': 'notNone',
            'someThings': [{'ruleVersion': f'{i}.{j}'} for j in range(NUMBER_OF_ITEMS_PER_PAGE)]
        } for i in range(MAX_PAGES + 10)
    ]

    @api_helpers.api_call_with_debug_logs
    @api_helpers.paginated_api_call('someThings', max_pages=MAX_PAGES)
    def call_test_fn(nextToken=None):
        return test_fn(nextToken)

    response = call_test_fn()
    assert len(response['someThings']) == NUMBER_OF_ITEMS_PER_PAGE * MAX_PAGES
    assert test_fn.call_count == MAX_PAGES


def test_paginated_api_call_matches_criteria():
    test_fn = MagicMock()
    test_fn.side_effect = [
        {
            'nextToken': 'notNone',
            'someThings': [{'someAttribute': f'{i}'} for i in range(NUMBER_OF_ITEMS_PER_PAGE)]
        } for _ in range(MAX_PAGES)
    ]

    # only keep items if someAttribute is '0'
    def criteria(_, item):
        return item.get('someAttribute', '') == '0'

    @api_helpers.api_call_with_debug_logs
    @api_helpers.paginated_api_call('someThings', criteria_to_keep=criteria, max_pages=MAX_PAGES)
    def call_test_fn(nextToken=None):
        return test_fn(nextToken)

    response = call_test_fn()

    # The criteria is for someAttribute = 0, so only one 'someThing' per page meets the criteria
    assert len(response['someThings']) == MAX_PAGES
    assert test_fn.call_count == MAX_PAGES
