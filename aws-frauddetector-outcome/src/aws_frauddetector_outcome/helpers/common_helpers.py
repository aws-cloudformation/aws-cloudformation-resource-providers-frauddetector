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


# Outcomes


def put_outcome_and_return_progress(frauddetector_client, model, progress):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
            api_helpers.call_put_outcome(
                frauddetector_client,
                outcome_name=model.Name,
                outcome_tags=tags,
                outcome_description=model.Description,
            )
        else:
            api_helpers.call_put_outcome(
                frauddetector_client,
                outcome_name=model.Name,
                outcome_description=model.Description,
            )
        progress.resourceModel = model_helpers.get_outcomes_and_return_model_for_outcome(
            frauddetector_client, model.Name
        )
        progress.status = OperationStatus.SUCCESS
        LOG.info(f"just finished a put outcome call: {progress.resourceModel}")
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
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
