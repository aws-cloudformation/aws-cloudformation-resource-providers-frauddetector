from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
)
from typing import List
from ..models import Tag
from . import model_helpers, api_helpers, validation_helpers

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
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


# EntityTypes


def put_entity_type_and_return_progress(frauddetector_client, model, progress):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
            api_helpers.call_put_entity_type(
                frauddetector_client,
                entity_type_name=model.Name,
                entity_type_tags=tags,
                entity_type_description=model.Description,
            )
        else:
            api_helpers.call_put_entity_type(
                frauddetector_client,
                entity_type_name=model.Name,
                entity_type_description=model.Description,
            )
        progress.resourceModel = model_helpers.get_entity_types_and_return_model_for_entity_type(
            frauddetector_client, model.Name
        )
        progress.status = OperationStatus.SUCCESS
        LOG.info(f"just finished a put entity_type call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


# Labels


def put_label_and_return_progress(frauddetector_client, model, progress):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
            api_helpers.call_put_label(
                frauddetector_client,
                label_name=model.Name,
                label_tags=tags,
                label_description=model.Description,
            )
        else:
            api_helpers.call_put_label(
                frauddetector_client,
                label_name=model.Name,
                label_description=model.Description,
            )
        progress.resourceModel = model_helpers.get_labels_and_return_model_for_label(frauddetector_client, model.Name)
        progress.status = OperationStatus.SUCCESS
        LOG.info(f"just finished a put label call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


# Variables


def create_variable_and_return_progress(frauddetector_client, model, progress):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
        else:
            tags = None
        api_helpers.call_create_variable(
            frauddetector_client,
            variable_name=model.Name,
            variable_tags=tags,
            variable_data_type=model.DataType,
            variable_data_source=model.DataSource,
            variable_default_value=model.DefaultValue,
            variable_type=model.VariableType,
            variable_description=model.Description,
        )
        progress.resourceModel = model_helpers.get_variables_and_return_model_for_variable(
            frauddetector_client, model.Name
        )
        progress.status = OperationStatus.SUCCESS
        LOG.info(f"just finished a create variable call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def update_variable_and_return_progress(frauddetector_client, model, progress):
    try:
        api_helpers.call_update_variable(
            frauddetector_client,
            variable_name=model.Name,
            variable_default_value=model.DefaultValue,
            variable_description=model.Description,
        )
        progress.resourceModel = model_helpers.get_variables_and_return_model_for_variable(
            frauddetector_client, model.Name
        )
        progress.status = OperationStatus.SUCCESS
        LOG.info(f"just finished a create variable call: {progress.resourceModel}")
    except RuntimeError as e:
        progress.status = OperationStatus.FAILED
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
