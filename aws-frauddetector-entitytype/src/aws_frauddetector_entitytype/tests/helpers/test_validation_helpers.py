from ...helpers import validation_helpers
from botocore.exceptions import ClientError
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_check_if_get_entity_types_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_entity_types.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
    ]

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_entity_types_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_entity_types_response = {"entityTypes": [unit_test_utils.FAKE_ENTITY_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_entity_types_response
