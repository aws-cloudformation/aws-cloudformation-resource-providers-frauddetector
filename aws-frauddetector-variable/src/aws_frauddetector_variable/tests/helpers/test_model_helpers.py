from ...helpers import model_helpers
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_get_model_for_variable():
    # Arrange
    list_tags_response = {'tags': unit_test_utils.FAKE_TAGS}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)

    # Act
    model_for_variable = model_helpers.get_model_for_variable(mock_afd_client, unit_test_utils.FAKE_IP_VARIABLE)

    # Assert
    assert mock_afd_client.list_tags_for_resource.call_count == 1
    assert model_for_variable == unit_test_utils.create_fake_model(is_output_model=True)
