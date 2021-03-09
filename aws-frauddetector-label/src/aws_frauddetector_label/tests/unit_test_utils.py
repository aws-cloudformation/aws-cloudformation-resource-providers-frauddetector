from ..models import ResourceModel, Tag
from cloudformation_cli_python_lib import SessionProxy, ProgressEvent, OperationStatus
from unittest.mock import MagicMock

FAKE_ARN = 'arn:aws:frauddetector:afdresourcetype:123456789012:afdresourcename'
FAKE_ARN_PREFIX = 'arn:aws:frauddetector:afdresourcetype:123456789012:'
FAKE_NAME = 'afdresourcename'
FAKE_TIME = 'faketime'
FRAUD = 'FRAUD'
LEGIT = 'LEGIT'
IP_LOWER = 'ip'
EMAIL_LOWER = 'email'
EVENT = 'EVENT'
STRING = 'STRING'
DEFAULT = 'DEFAULT'
IP_ADDRESS = 'IP_ADDRESS'
EMAIL_ADDRESS = 'EMAIL_ADDRESS'
FAKE_TAG_MODELS = [
    Tag(Key='cfnunittest', Value='1')
]
FAKE_TAGS = [
    {'key': 'cfnunittest', 'value': '1'}
]
FAKE_TAG_MODELS_DIFFERENT = [
    Tag(Key='cfnunittest', Value='different_value'),
    Tag(Key='new_key', Value='value'),
]
FAKE_TAGS_DIFFERENT = [
    {'key': 'cfnunittest', 'value': 'different_value'},
    {'key': 'new_key', 'value': 'value'}
]
FAKE_DESCRIPTION = 'a cfnunittest description'
FAKE_OUTCOME = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': FAKE_NAME
}
FAKE_ENTITY_TYPE = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': FAKE_NAME
}
FAKE_FRAUD_LABEL = {
    'arn': f'{FAKE_ARN_PREFIX}{FRAUD}',
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': FRAUD
}
FAKE_LEGIT_LABEL = {
    'arn': f'{FAKE_ARN_PREFIX}{LEGIT}',
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': LEGIT
}
FAKE_IP_VARIABLE = {
    'arn': f'{FAKE_ARN_PREFIX}{IP_LOWER}',
    'createdTime': FAKE_TIME,
    'dataSource': EVENT,
    'dataType': STRING,
    'defaultValue': DEFAULT,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': IP_LOWER,
    'variableType': IP_ADDRESS
}
FAKE_EMAIL_VARIABLE = {
    'arn': f'{FAKE_ARN_PREFIX}{EMAIL_LOWER}',
    'createdTime': FAKE_TIME,
    'dataSource': EVENT,
    'dataType': STRING,
    'defaultValue': DEFAULT,
    'description': FAKE_DESCRIPTION,
    'lastUpdatedTime': FAKE_TIME,
    'name': EMAIL_LOWER,
    'variableType': EMAIL_ADDRESS
}
FAKE_VARIABLE_ENTRIES = [
    {
        'dataSource': EVENT,
        'dataType': STRING,
        'defaultValue': DEFAULT,
        'description': FAKE_DESCRIPTION,
        'name': EMAIL_LOWER,
        'variableType': EVENT
    },
    {
        'dataSource': EVENT,
        'dataType': STRING,
        'defaultValue': DEFAULT,
        'description': FAKE_DESCRIPTION,
        'name': IP_LOWER,
        'variableType': EVENT
    }
]
FAKE_EVENT_TYPE = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'entityTypes': [FAKE_NAME],
    'eventVariables': [FAKE_IP_VARIABLE.get('name'), FAKE_EMAIL_VARIABLE.get('name')],
    'labels': [FRAUD, LEGIT],
    'lastUpdatedTime': FAKE_TIME,
    'name': FAKE_NAME
}
FAKE_DETECTOR = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'detectorId': FAKE_NAME,
    'eventTypeName': FAKE_NAME,
    'lastUpdatedTime': FAKE_TIME
}


def create_in_progress_progress(model):
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )


def create_fake_model(is_output_model: bool = False):
    return ResourceModel(
        Name=FRAUD,
        Arn=[None, f'{FAKE_ARN_PREFIX}{FRAUD}'][is_output_model],
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model]
    )


def create_fake_variable():
    return {
        'arn': f'{FAKE_ARN_PREFIX}{IP_LOWER}',
        'createdTime': FAKE_TIME,
        'dataSource': EVENT,
        'dataType': STRING,
        'defaultValue': DEFAULT,
        'description': FAKE_DESCRIPTION,
        'lastUpdatedTime': FAKE_TIME,
        'name': IP_LOWER,
        'variableType': IP_ADDRESS
    }


def create_mock_afd_client():
    mock_afd_client = MagicMock(name="mock_afd_client")
    return mock_afd_client


def create_mock_session(mock_afd_client):
    mock_session_impl = MagicMock(name='mock_session_impl')
    mock_session_impl.client = MagicMock(return_value=mock_afd_client)
    mock_session = SessionProxy(session=mock_session_impl)
    return mock_session
