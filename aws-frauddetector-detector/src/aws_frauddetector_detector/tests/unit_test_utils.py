from .. import models
from cloudformation_cli_python_lib import SessionProxy, ProgressEvent, OperationStatus
from unittest.mock import MagicMock

FAKE_ARN = 'arn:aws:frauddetector:region:123456789012:afdresourcetype/afdresourcename'
FAKE_ARN_PREFIX = 'arn:aws:frauddetector:region:123456789012:afdresourcetype/'
FAKE_NAME = 'afdresourcename'
FAKE_ACTIVE_DV_STATUS = 'ACTIVE'
FAKE_DRAFT_DV_STATUS = 'DRAFT'
FAKE_VERSION_ID = '1'
FAKE_RULE_EXECUTION_MODE = 'ALL_MATCHED'
FAKE_RULE_LANGUAGE = 'DETECTORPL'
FAKE_EXPRESSION = ''
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
    models.Tag(Key='cfnunittest', Value='1')
]
FAKE_TAGS = [
    {'key': 'cfnunittest', 'value': '1'}
]
FAKE_TAG_MODELS_DIFFERENT = [
    models.Tag(Key='cfnunittest', Value='different_value'),
    models.Tag(Key='new_key', Value='value'),
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
FAKE_DETECTOR_VERSION = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'detectorId': FAKE_NAME,
    'detectorVersionId': FAKE_VERSION_ID,
    'externalModelEndpoints': [],
    'lastUpdatedTime': FAKE_TIME,
    'modelVersions': [],
    'ruleExecutionMode': FAKE_RULE_EXECUTION_MODE,
    'rules': [
        {
            'detectorId': FAKE_NAME,
            'ruleId': FAKE_NAME,
            'ruleVersion': FAKE_VERSION_ID
        }
    ],
    'status': FAKE_ACTIVE_DV_STATUS
}
FAKE_NEW_DETECTOR_VERSION = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'detectorId': FAKE_NAME,
    'detectorVersionId': '2',
    'externalModelEndpoints': [],
    'lastUpdatedTime': FAKE_TIME,
    'modelVersions': [],
    'ruleExecutionMode': FAKE_RULE_EXECUTION_MODE,
    'rules': [
        {
            'detectorId': FAKE_NAME,
            'ruleId': FAKE_NAME,
            'ruleVersion': FAKE_VERSION_ID
        }
    ],
    'status': FAKE_ACTIVE_DV_STATUS
}
FAKE_RULE_DETAIL = {
    'arn': FAKE_ARN,
    'createdTime': FAKE_TIME,
    'description': FAKE_DESCRIPTION,
    'detectorId': FAKE_NAME,
    'ruleId': FAKE_NAME,
    'ruleVersion': FAKE_VERSION_ID,
    'outcomes': [FAKE_OUTCOME.get('name')],
    'expression': FAKE_EXPRESSION,
    'language': FAKE_RULE_LANGUAGE,
    'lastUpdatedTime': FAKE_TIME
}


def create_in_progress_progress(model):
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model
    )


def create_fake_entity_type_model(is_output_model: bool = False):
    return models.EntityType(
        Name=FAKE_NAME,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Inline=True,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model]
    )


def create_fake_referenced_entity_type_model(is_output_model: bool = False):
    return models.EntityType(
        Name=[None, FAKE_NAME][is_output_model],
        Description=None,
        Tags=None,
        Inline=False,
        Arn=FAKE_ARN,
        CreatedTime=None,
        LastUpdatedTime=None
    )


def create_fake_label_model(is_output_model: bool = False, is_fraud: bool = False):
    label_name = [LEGIT, FRAUD][is_fraud]
    return models.Label(
        Name=label_name,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Inline=True,
        Arn=[None, f"{FAKE_ARN_PREFIX}{label_name}"][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model]
    )


def create_fake_referenced_label_model(is_output_model: bool = False, is_fraud: bool = False):
    label_name = [LEGIT, FRAUD][is_fraud]
    return models.Label(
        Name=[None, label_name][is_output_model],
        Description=None,
        Tags=None,
        Inline=False,
        Arn=f"{FAKE_ARN_PREFIX}{label_name}",
        CreatedTime=None,
        LastUpdatedTime=None
    )


def create_fake_event_variable(is_output_model: bool = False, is_ip: bool = False):
    variable_name = [EMAIL_LOWER, IP_LOWER][is_ip]
    variable_type = [EMAIL_ADDRESS, IP_ADDRESS][is_ip]
    return models.EventVariable(
        Name=variable_name,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Inline=True,
        Arn=[None, f"{FAKE_ARN_PREFIX}{variable_name}"][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        DataSource=EVENT,
        DataType=STRING,
        DefaultValue=DEFAULT,
        VariableType=variable_type
    )


def create_fake_referenced_event_variable(is_output_model: bool = False, is_ip: bool = False):
    variable_name = [EMAIL_LOWER, IP_LOWER][is_ip]
    return models.EventVariable(
        Name=[None, variable_name][is_output_model],
        Description=None,
        Tags=None,
        Inline=False,
        Arn=f"{FAKE_ARN_PREFIX}{variable_name}",
        CreatedTime=None,
        LastUpdatedTime=None,
        DataSource=None,
        DataType=None,
        DefaultValue=None,
        VariableType=None
    )


def create_fake_outcome(is_output_model: bool = False):
    return models.Outcome(
        Name=FAKE_NAME,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Inline=True,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model]
    )


def create_fake_referenced_outcome(is_output_model: bool = False):
    return models.Outcome(
        Name=[None, FAKE_NAME][is_output_model],
        Description=None,
        Tags=None,
        Inline=False,
        Arn=FAKE_ARN,
        CreatedTime=None,
        LastUpdatedTime=None
    )


def create_fake_event_type(is_output_model: bool = False):
    return models.EventType(
        Name=FAKE_NAME,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        EntityTypes=[create_fake_entity_type_model(is_output_model)],
        Labels=[
            create_fake_label_model(is_output_model, True),
            create_fake_label_model(is_output_model, False)
        ],
        EventVariables=[
            create_fake_event_variable(is_output_model, True),
            create_fake_event_variable(is_output_model, False)
        ],
        Inline=True
    )


def create_fake_inline_event_type_with_referenced_dependencies(is_output_model: bool = False):
    return models.EventType(
        Name=FAKE_NAME,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        EntityTypes=[create_fake_referenced_entity_type_model(is_output_model)],
        Labels=[
            create_fake_referenced_label_model(is_output_model, True),
            create_fake_referenced_label_model(is_output_model, False)
        ],
        EventVariables=[
            create_fake_referenced_event_variable(is_output_model, True),
            create_fake_referenced_event_variable(is_output_model, False)
        ],
        Inline=True
    )


def create_fake_referenced_event_type(is_output_model: bool = False):
    return models.EventType(
        Name=[None, FAKE_NAME][is_output_model],
        Description=None,
        Tags=None,
        Arn=FAKE_ARN,
        CreatedTime=None,
        LastUpdatedTime=None,
        EntityTypes=None,
        Labels=None,
        EventVariables=None,
        Inline=False
    )


def create_fake_rule(is_output_model: bool = False):
    return models.Rule(
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        RuleVersion=[None, FAKE_VERSION_ID][is_output_model],
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        DetectorId=FAKE_NAME,
        Expression=FAKE_EXPRESSION,
        Language=FAKE_RULE_LANGUAGE,
        Outcomes=[create_fake_outcome(is_output_model)],
        RuleId=FAKE_NAME
    )


def create_fake_rule_with_referenced_outcome(is_output_model: bool = False):
    return models.Rule(
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        RuleVersion=[None, FAKE_VERSION_ID][is_output_model],
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        DetectorId=FAKE_NAME,
        Expression=FAKE_EXPRESSION,
        Language=FAKE_RULE_LANGUAGE,
        Outcomes=[create_fake_referenced_outcome(is_output_model)],
        RuleId=FAKE_NAME
    )


def create_fake_model(is_output_model: bool = False):
    return models.ResourceModel(
        DetectorId=FAKE_NAME,
        DetectorVersionId=[None, FAKE_VERSION_ID][is_output_model],
        DetectorVersionStatus=FAKE_ACTIVE_DV_STATUS,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        RuleExecutionMode=FAKE_RULE_EXECUTION_MODE,
        Rules=[create_fake_rule(is_output_model)],
        EventType=create_fake_event_type(is_output_model)
    )


def create_fake_model_with_references(is_output_model: bool = False):
    return models.ResourceModel(
        DetectorId=FAKE_NAME,
        DetectorVersionId=[None, FAKE_VERSION_ID][is_output_model],
        DetectorVersionStatus=FAKE_ACTIVE_DV_STATUS,
        Description=FAKE_DESCRIPTION,
        Tags=FAKE_TAG_MODELS,
        Arn=[None, FAKE_ARN][is_output_model],
        CreatedTime=[None, FAKE_TIME][is_output_model],
        LastUpdatedTime=[None, FAKE_TIME][is_output_model],
        RuleExecutionMode=FAKE_RULE_EXECUTION_MODE,
        Rules=[create_fake_rule_with_referenced_outcome(is_output_model)],
        EventType=create_fake_referenced_event_type(is_output_model)
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


def create_mock_session():
    mock_session_impl = MagicMock(name='mock_session_impl')
    mock_session_impl.client = MagicMock(return_value=MagicMock(name="mock_afd_client"))
    mock_session = SessionProxy(session=mock_session_impl)
    return mock_session
