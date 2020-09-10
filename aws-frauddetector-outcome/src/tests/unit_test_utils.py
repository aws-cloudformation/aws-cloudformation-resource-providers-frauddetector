from aws_frauddetector_outcome.models import ResourceModel, Tag
from cloudformation_cli_python_lib import SessionProxy, ProgressEvent, OperationStatus
from unittest.mock import MagicMock

FAKE_ARN = 'arn:aws:frauddetector:outcome:123456789012:cfnunittestoutcome'
FAKE_NAME = 'cfnunittestoutcome'
FAKE_TIME = 'fake'
FAKE_TAG_MODELS = [
    Tag(Key='cfnunittest', Value='1')
]
FAKE_TAGS = [
    {'key': 'cfnunittest', 'value': '1'}
]
FAKE_DESCRIPTION = 'a cfnunittest description'
FAKE_OUTCOME = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': FAKE_NAME
}


def create_in_progress_progress(model):
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )


def create_fake_model(is_output_model: bool = False):
    return ResourceModel(
        Name=FAKE_NAME,
        Arn=[None, FAKE_ARN][is_output_model],
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model]
    )


def create_mock_afd_client():
    mock_afd_client = MagicMock(name="mock_afd_client")
    return mock_afd_client


def create_mock_session(mock_afd_client):
    mock_session_impl = MagicMock(name='mock_session_impl')
    mock_session_impl.client = MagicMock(return_value=mock_afd_client)
    mock_session = SessionProxy(session=mock_session_impl)
    return mock_session
