from ...helpers import client_helpers
from .. import unit_test_utils
import pytest
from cloudformation_cli_python_lib.exceptions import InternalFailure


def test_get_afd_client_returns_unique_client():
    # Arrange
    mock_session_1 = unit_test_utils.create_mock_session()
    mock_session_2 = unit_test_utils.create_mock_session()

    # Act
    afd_client_1 = client_helpers.get_afd_client(mock_session_1)
    afd_client_2 = client_helpers.get_afd_client(mock_session_2)

    # Assert
    assert mock_session_1 is not mock_session_2
    assert afd_client_1 is not afd_client_2


def test_get_afd_client_throws_internal_failure_exception():
    with pytest.raises(InternalFailure):
        client_helpers.get_afd_client("")
