from ...helpers import model_helpers
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_get_model_for_list():
    # Arrange
    list_tags_response = {"tags": unit_test_utils.FAKE_TAGS}
    get_list_elements_response = {"elements": []}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.get_list_elements = MagicMock(return_value=get_list_elements_response)

    # Act
    model_for_list = model_helpers.get_model_for_list(mock_afd_client, unit_test_utils.FAKE_LIST)

    # Assert
    assert mock_afd_client.list_tags_for_resource.call_count == 1
    assert model_for_list == unit_test_utils.create_fake_model(is_output_model=True)
