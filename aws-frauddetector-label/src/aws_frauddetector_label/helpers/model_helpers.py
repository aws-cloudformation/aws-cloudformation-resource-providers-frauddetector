from typing import List
from cloudformation_cli_python_lib import exceptions
from ..models import ResourceModel, Tag
from . import api_helpers

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


def get_tags_from_tag_models(tag_models: List[Tag]):
    # boto3 afd client doesn't know about the 'Tags' class that cfn creates
    return [{"key": tag.Key, "value": tag.Value} for tag in tag_models]


def get_tag_models_from_tags(tags: List[dict]):
    # we need to translate our afd tags back to a list of cfn Tag
    return [Tag(Key=tag.get('key', ''), Value=tag.get('value', '')) for tag in tags]


def get_model_for_label(frauddetector_client, label):
    label_arn = label.get('arn', '')
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=label_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=label.get('name', ''),
        Arn=label_arn,
        Tags=tag_models,
        Description=label.get('description', ''),
        CreatedTime=label.get('createdTime', ''),
        LastUpdatedTime=label.get('lastUpdatedTime', '')
    )


def get_labels_and_return_model_for_label(frauddetector_client, label_name):
    try:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name=label_name)
        labels = get_labels_response.get('labels', [])
        if len(labels) > 0:
            return get_model_for_label(frauddetector_client, labels[0])
        # if get labels worked but did not return any labels, we have major problems
        error_msg = f"get_labels for {label_name} worked but did not return any labels!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an label: {e}")
