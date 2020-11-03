from ...helpers import client_helpers
from .. import unit_test_utils


def test_get_singleton_afd_client_always_same_client():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_session = unit_test_utils.create_mock_session(mock_afd_client)
    mock_session_2 = unit_test_utils.create_mock_session(mock_afd_client)

    # Act
    returned_afd_client = client_helpers.get_singleton_afd_client(mock_session)
    returned_afd_client_2 = client_helpers.get_singleton_afd_client(mock_session_2)
    returned_afd_client_3 = client_helpers.get_singleton_afd_client(mock_session)

    # Assert
    assert mock_session is not mock_session_2
    assert mock_afd_client is returned_afd_client
    assert returned_afd_client is returned_afd_client_2
    assert returned_afd_client_2 is returned_afd_client_3
