from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
)
from typing import List
from ..models import Tag
from . import model_helpers, api_helpers

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

# Lists


def create_list_and_return_progress(frauddetector_client, model, progress):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
        else:
            tags = None
        api_helpers.call_create_list(
            frauddetector_client,
            list_name=model.Name,
            list_tags=tags,
            list_description=model.Description,
            list_elements=model.Elements,
            list_variable_type=model.VariableType,
        )
        _return_success(frauddetector_client, model, progress)
        LOG.info(f"just finished a create list call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def update_list_and_return_progress(frauddetector_client, model, progress):
    try:
        api_helpers.call_update_list(
            frauddetector_client,
            list_name=model.Name,
            list_description=model.Description,
            list_elements=model.Elements,
            list_variable_type=model.VariableType,
        )
        _return_success(frauddetector_client, model, progress)
        LOG.info(f"just finished an update list call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def _return_success(frauddetector_client, model, progress):
    progress.resourceModel = model_helpers.get_lists_and_return_model_for_list(frauddetector_client, model.Name)
    progress.status = OperationStatus.SUCCESS
    return progress


# Tags


def update_tags(frauddetector_client, afd_resource_arn: str, new_tags: List[Tag] = None):
    try:
        list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, afd_resource_arn)
        attached_tags = list_tags_response.get("tags", [])
        attached_tags_dict = {tag.get("key", ""): tag.get("value", None) for tag in attached_tags}

        tags_to_add = [model_helpers.get_tags_from_tag_models(new_tags), {}][new_tags is None]
        tags_to_add_dict = {tag.get("key", ""): tag.get("value", None) for tag in tags_to_add}

        if attached_tags_dict == tags_to_add_dict:
            return

        if attached_tags:
            api_helpers.call_untag_resource(frauddetector_client, afd_resource_arn, list(attached_tags_dict.keys()))
        if tags_to_add_dict:
            api_helpers.call_tag_resource(frauddetector_client, afd_resource_arn, tags_to_add)

    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while updating tags: {e}")
