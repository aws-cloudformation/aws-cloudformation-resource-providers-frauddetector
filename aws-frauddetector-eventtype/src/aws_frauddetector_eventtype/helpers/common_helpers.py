from cloudformation_cli_python_lib import OperationStatus, exceptions, ProgressEvent
from functools import partial
from typing import List, Callable, Tuple
from .. import models
from . import model_helpers, api_helpers, validation_helpers, util

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


# Event Types


def put_event_type_and_return_progress(frauddetector_client, model, progress: ProgressEvent):
    try:
        if hasattr(model, "Tags"):
            tags = model_helpers.get_tags_from_tag_models(model.Tags)
            put_event_type_func = partial(
                api_helpers.call_put_event_type,
                frauddetector_client=frauddetector_client,
                event_type_tags=tags,
            )
        else:
            put_event_type_func = partial(
                api_helpers.call_put_event_type,
                frauddetector_client=frauddetector_client,
            )

        put_event_type_for_model(put_event_type_func, model)
        progress.resourceModel = model_helpers.get_event_type_and_return_model(frauddetector_client, model)
        progress.status = OperationStatus.SUCCESS
        LOG.debug(f"just finished a put event_type call for event type: {progress.resourceModel.Name}")

    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def put_event_type_for_model(put_event_type_func: Callable, model: models.ResourceModel):
    # get entity names
    event_variable_names = [
        [util.extract_name_from_arn(var.Arn), var.Name][var.Arn is None] for var in model.EventVariables
    ]
    entity_type_names = [
        [util.extract_name_from_arn(entity_type.Arn), entity_type.Name][entity_type.Arn is None]
        for entity_type in model.EntityTypes
    ]
    label_names = [[util.extract_name_from_arn(label.Arn), label.Name][label.Arn is None] for label in model.Labels]

    # call put event type
    put_event_type_func(
        event_type_name=model.Name,
        entity_type_names=entity_type_names,
        event_variable_names=event_variable_names,
        label_names=label_names,
        event_type_description=model.Description,
    )


# Variables


def create_inline_event_variable(frauddetector_client, event_variable: models.EventVariable):
    if hasattr(event_variable, "Tags"):
        tags = model_helpers.get_tags_from_tag_models(event_variable.Tags)
        create_variable_func = partial(
            api_helpers.call_create_variable,
            frauddetector_client=frauddetector_client,
            variable_tags=tags,
        )
    else:
        create_variable_func = partial(api_helpers.call_create_variable, frauddetector_client=frauddetector_client)
    create_variable_func(
        variable_name=event_variable.Name,
        variable_data_source=event_variable.DataSource,
        variable_data_type=event_variable.DataType,
        variable_default_value=event_variable.DefaultValue,
        variable_description=event_variable.Description,
        variable_type=event_variable.VariableType,
    )


def create_inline_event_variables(frauddetector_client, event_variables: List[models.EventVariable]):
    LOG.info(f"creating inline event variables: {event_variables}")
    tags, variable_entries = _get_tags_and_variable_entries_from_inline_event_variables(event_variables)
    api_helpers.call_batch_create_variable(frauddetector_client, variable_entries=variable_entries, tags=tags)


def _get_tags_and_variable_entries_from_inline_event_variables(
    event_variables: List[models.EventVariable],
) -> Tuple[list, list]:
    """
    This function takes in a list of event variables and returns a list of tags and a list of variable entries
    """
    tags = []
    variable_entries = []
    for event_variable in event_variables:
        if not event_variable.Inline:
            continue
        new_tags = model_helpers.get_tags_from_tag_models(event_variable.Tags)
        if new_tags:
            tags.extend(new_tags)
        variable_entries.append(
            {
                "dataSource": event_variable.DataSource,
                "dataType": event_variable.DataType,
                "defaultValue": event_variable.DefaultValue,
                "description": event_variable.Description,
                "name": event_variable.Name,
                "variableType": event_variable.VariableType,
            }
        )
    return tags, variable_entries


# Labels


def put_inline_label(frauddetector_client, label):
    if hasattr(label, "Tags"):
        tags = model_helpers.get_tags_from_tag_models(label.Tags)
        put_label_func = partial(
            api_helpers.call_put_label,
            frauddetector_client=frauddetector_client,
            label_tags=tags,
        )
    else:
        put_label_func = partial(api_helpers.call_put_label, frauddetector_client=frauddetector_client)
    put_label_func(label_name=label.Name, label_description=label.Description)


# Entity Types


def put_inline_entity_type(frauddetector_client, entity_type):
    if hasattr(entity_type, "Tags"):
        tags = model_helpers.get_tags_from_tag_models(entity_type.Tags)
        put_entity_type_func = partial(
            api_helpers.call_put_entity_type,
            frauddetector_client=frauddetector_client,
            entity_type_tags=tags,
        )
    else:
        put_entity_type_func = partial(api_helpers.call_put_entity_type, frauddetector_client=frauddetector_client)
    put_entity_type_func(
        entity_type_name=entity_type.Name,
        entity_type_description=entity_type.Description,
    )


# Tags


def update_tags(frauddetector_client, afd_resource_arn: str, new_tags: List[models.Tag] = None):
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
