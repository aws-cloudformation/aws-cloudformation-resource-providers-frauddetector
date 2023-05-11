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


# Lists


def get_model_for_list(frauddetector_client, list):
    list_arn = list.get("arn", "")
    list_name = list.get("name", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=list_arn)
    list_elements_response = api_helpers.call_get_list_elements(frauddetector_client, list_name)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    model_to_return = ResourceModel(
        Name=list_name,
        Arn=list_arn,
        Tags=tag_models,
        Description=list.get("description", ""),
        VariableType=list.get("variableType", None),
        CreatedTime=list.get("createdTime", ""),
        LastUpdatedTime=list.get("lastUpdatedTime", ""),
        Elements=[],
    )
    if list_elements_response:
        model_to_return.Elements = list_elements_response.get("elements", [])
    return model_to_return


def get_lists_and_return_model_for_list(frauddetector_client, list_name):
    try:
        get_lists_metadata_response = api_helpers.call_get_lists_metadata(frauddetector_client, list_name=list_name)
        lists = get_lists_metadata_response.get("lists", [])
        if lists:
            return get_model_for_list(frauddetector_client, lists[0])
        # if get variables worked but did not return any variables, we have major problems
        error_msg = f"get_lists_metadata for {list_name} worked but did not return any lists!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting a list: {e}")
