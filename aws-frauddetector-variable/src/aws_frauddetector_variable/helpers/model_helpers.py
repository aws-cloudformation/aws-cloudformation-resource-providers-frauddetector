from typing import List, Optional
from cloudformation_cli_python_lib import (
    exceptions,
)

from ..models import ResourceModel, Tag
from . import api_helpers

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


# Tags


def get_tags_from_tag_models(tag_models: Optional[List[Tag]]) -> Optional[List[dict]]:
    # boto3 afd client doesn't know about the 'Tags' class that cfn creates
    if tag_models is None:
        return None
    return [{"key": tag.Key, "value": tag.Value} for tag in tag_models]


def get_tag_models_from_tags(tags: Optional[List[dict]]) -> Optional[List[Tag]]:
    # we need to translate our afd tags back to a list of cfn Tag
    if tags is None:
        return None
    return [Tag(Key=tag.get("key", ""), Value=tag.get("value", "")) for tag in tags]


def _get_tags_for_given_arn(frauddetector_client, arn):
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, arn)
    return list_tags_response.get("tags", [])


# Variables


def get_model_for_variable(frauddetector_client, variable):
    variable_arn = variable.get("arn", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=variable_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=variable.get("name", ""),
        Arn=variable_arn,
        Tags=tag_models,
        Description=variable.get("description", ""),
        DataType=variable.get("dataType", ""),
        DataSource=variable.get("dataSource", ""),
        DefaultValue=variable.get("defaultValue", ""),
        VariableType=variable.get("variableType", ""),
        CreatedTime=variable.get("createdTime", ""),
        LastUpdatedTime=variable.get("lastUpdatedTime", ""),
    )


def get_variables_and_return_model_for_variable(frauddetector_client, variable_name):
    try:
        get_variables_response = api_helpers.call_get_variables(frauddetector_client, variable_name=variable_name)
        variables = get_variables_response.get("variables", [])
        if variables:
            return get_model_for_variable(frauddetector_client, variables[0])
        # if get variables worked but did not return any variables, we have major problems
        error_msg = f"get_variables for {variable_name} worked but did not return any variables!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an variable: {e}")
