from typing import List, Optional
from cloudformation_cli_python_lib import (
    OperationStatus,
    SessionProxy,
    exceptions,
)

from ..models import ResourceModel, EventVariable, Tag, ResourceModelForVariable
from . import api_helpers, validation_helpers

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


# Outcomes


def get_model_for_outcome(frauddetector_client, outcome):
    outcome_arn = outcome.get("arn", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=outcome_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=outcome.get("name", ""),
        Arn=outcome_arn,
        Tags=tag_models,
        Description=outcome.get("description", ""),
        CreatedTime=outcome.get("createdTime", ""),
        LastUpdatedTime=outcome.get("lastUpdatedTime", ""),
    )


def get_outcomes_and_return_model_for_outcome(frauddetector_client, outcome_name):
    try:
        get_outcomes_response = api_helpers.call_get_outcomes(frauddetector_client, outcome_name=outcome_name)
        outcomes = get_outcomes_response.get("outcomes", [])
        if outcomes:
            return get_model_for_outcome(frauddetector_client, outcomes[0])
        # if get outcomes worked but did not return any outcomes, we have major problems
        error_msg = f"get_outcomes for {outcome_name} worked but did not return any outcomes!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an outcome: {e}")


# Labels


def get_model_for_label(frauddetector_client, label):
    label_arn = label.get("arn", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=label_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=label.get("name", ""),
        Arn=label_arn,
        Tags=tag_models,
        Description=label.get("description", ""),
        CreatedTime=label.get("createdTime", ""),
        LastUpdatedTime=label.get("lastUpdatedTime", ""),
    )


def get_labels_and_return_model_for_label(frauddetector_client, label_name):
    try:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name=label_name)
        labels = get_labels_response.get("labels", [])
        if labels:
            return get_model_for_label(frauddetector_client, labels[0])
        # if get labels worked but did not return any labels, we have major problems
        error_msg = f"get_labels for {label_name} worked but did not return any labels!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an label: {e}")


# EntityTypes


def get_model_for_entity_type(frauddetector_client, entity_type):
    entity_type_arn = entity_type.get("arn", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=entity_type_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=entity_type.get("name", ""),
        Arn=entity_type_arn,
        Tags=tag_models,
        Description=entity_type.get("description", None),
        CreatedTime=entity_type.get("createdTime", ""),
        LastUpdatedTime=entity_type.get("lastUpdatedTime", ""),
    )


def get_entity_types_and_return_model_for_entity_type(frauddetector_client, entity_type_name):
    try:
        get_entity_types_response = api_helpers.call_get_entity_types(
            frauddetector_client, entity_type_name=entity_type_name
        )
        entity_types = get_entity_types_response.get("entityTypes", [])
        if entity_types:
            return get_model_for_entity_type(frauddetector_client, entity_types[0])
        # if get entity_types worked but did not return any entity_types, we have major problems
        error_msg = f"get_entity_types for {entity_type_name} worked but did not return any entity_types!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an entity_type: {e}")


# Variables


def get_model_for_variable(frauddetector_client, variable):
    variable_arn = variable.get("arn", "")
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=variable_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModelForVariable(
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
