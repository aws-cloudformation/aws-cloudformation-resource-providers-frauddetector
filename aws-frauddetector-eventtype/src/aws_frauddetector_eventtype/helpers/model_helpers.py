from typing import List, Optional
from cloudformation_cli_python_lib import (
    OperationStatus,
    SessionProxy,
    exceptions,
)

from .. import models
from . import api_helpers, validation_helpers, util

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


# Tags


def get_tags_from_tag_models(tag_models: Optional[List[models.Tag]]) -> Optional[List[dict]]:
    # boto3 afd client doesn't know about the 'Tags' class that cfn creates
    if tag_models is None:
        return None
    return [{"key": tag.Key, "value": tag.Value} for tag in tag_models]


def get_tag_models_from_tags(tags: Optional[List[dict]]) -> Optional[List[models.Tag]]:
    # we need to translate our afd tags back to a list of cfn Tag
    if tags is None:
        return None
    return [models.Tag(Key=tag.get('key', ''), Value=tag.get('value', '')) for tag in tags]


def _get_tags_for_given_arn(frauddetector_client, arn):
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, arn)
    return list_tags_response.get("tags", [])


# EventTypes


def get_event_type_and_return_model(frauddetector_client, event_type_model: models.ResourceModel):
    event_type_name = event_type_model.Name
    referenced_resources = get_referenced_resources(event_type_model)
    try:
        get_event_types_response = api_helpers.call_get_event_types(frauddetector_client, event_type_name)
        event_types = get_event_types_response.get('eventTypes', [])
        if event_types:
            return get_model_for_event_type(frauddetector_client, event_types[0], referenced_resources)
        # if get event types worked but did not return any event types, we have major problems
        error_msg = f"get_event_types for {event_type_name} worked but did not return any event types!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an event type: {e}")


def get_model_for_event_type(frauddetector_client, event_type, referenced_resources: dict):
    # build model from event type
    model = models.ResourceModel(Name=event_type.get('name', ''),
                                 Tags=[],
                                 Description=event_type.get('description', ''),
                                 EventVariables=[],
                                 Labels=[],
                                 EntityTypes=[],
                                 Arn=event_type.get('arn', ''),
                                 CreatedTime=event_type.get('createdTime', ''),
                                 LastUpdatedTime=event_type.get('lastUpdatedTime', ''))

    # attach Tags
    event_type_arn = event_type.get('arn', '')
    event_type_tags = _get_tags_for_given_arn(frauddetector_client, event_type_arn)
    # TODO: reorder tags to the same order as the input model to work around contract test bug
    model.Tags = get_tag_models_from_tags(event_type_tags)

    # attach EventVariables
    event_variables = event_type.get('eventVariables', [])
    model.EventVariables = _get_variables_and_return_event_variables_model(frauddetector_client,
                                                                           event_variables,
                                                                           referenced_resources['event_variables'])

    # attach Labels
    event_type_labels = event_type.get('labels', [])
    model.Labels = _get_labels_and_return_labels_model(frauddetector_client,
                                                       event_type_labels,
                                                       referenced_resources['labels'])

    # attach EntityTypes
    event_type_entity_types = event_type.get('entityTypes', [])
    model.EntityTypes = _get_entity_types_and_return_entity_types_model(frauddetector_client,
                                                                        event_type_entity_types,
                                                                        referenced_resources['entity_types'])

    # remove empty description/tags
    if not model.Tags:
        del model.Tags
    if model.Description is None or model.Description == '':
        del model.Description

    # return model
    return model


# EventVariables


def _get_variables_and_return_event_variables_model(frauddetector_client, variable_names, reference_variable_names: set):
    collected_variables = []
    for variable_name in variable_names:
        # use singular get_variables to preserve order (transient contract test bug workaround)
        get_variables_response = api_helpers.call_get_variables(frauddetector_client, variable_name)
        collected_variables.extend(get_variables_response.get('variables', []))
    return _get_event_variables_model_for_given_variables(frauddetector_client,
                                                          collected_variables,
                                                          reference_variable_names)


def _get_event_variables_model_for_given_variables(frauddetector_client, variables, reference_variable_names: set):
    variable_models = []
    for variable in variables:
        variable_tags = _get_tags_for_given_arn(frauddetector_client, variable.get('arn', ''))
        tag_models = get_tag_models_from_tags(variable_tags)
        variable_name = util.extract_name_from_arn(variable.get('arn', ''))
        LOG.debug(f"checking if {variable_name} is in {reference_variable_names}")
        if variable_name in reference_variable_names:
            LOG.debug(f"in reference set, {variable_name} is not inline")
            variable_model = models.EventVariable(Arn=variable.get('arn', ''),
                                                  Name=variable_name,
                                                  Tags=None,
                                                  Description=None,
                                                  DataType=None,
                                                  DataSource=None,
                                                  DefaultValue=None,
                                                  VariableType=None,
                                                  CreatedTime=None,
                                                  LastUpdatedTime=None,
                                                  Inline=False)
        else:
            LOG.debug(f"not in reference set, {variable_name} is inline")
            variable_model = models.EventVariable(Name=variable.get('name', ''),
                                                  Tags=tag_models,
                                                  Description=variable.get('description', ''),
                                                  DataType=variable.get('dataType', ''),
                                                  DataSource=variable.get('dataSource', ''),
                                                  DefaultValue=variable.get('defaultValue', ''),
                                                  VariableType=variable.get('variableType', ''),
                                                  Arn=variable.get('arn', ''),
                                                  CreatedTime=variable.get('createdTime', ''),
                                                  LastUpdatedTime=variable.get('lastUpdatedTime', ''),
                                                  Inline=True)
        # remove empty description/tags
        if not variable_model.Tags:
            del variable_model.Tags
        if variable_model.Description is None or variable_model.Description == '':
            del variable_model.Description
        variable_models.append(variable_model)
    return variable_models


# Labels


def _get_labels_and_return_labels_model(frauddetector_client, label_names, reference_label_names: set):
    label_models = []
    for label_name in label_names:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name)
        labels = get_labels_response.get('labels', [])
        if not labels:
            raise RuntimeError(f"Error! Expected an existing label, but label did not exist! label name {label_name}")
        label = labels[0]
        label_arn = label.get('arn', '')
        LOG.debug(f"checking if {label_name} is in {reference_label_names}")
        if label_name in reference_label_names:
            LOG.debug(f"in reference set, {label_name} is not inline")
            label_model = models.Label(Arn=label_arn,
                                       Name=label_name,
                                       Tags=None,
                                       Description=None,
                                       CreatedTime=None,
                                       LastUpdatedTime=None,
                                       Inline=False)
        else:
            LOG.debug(f"not in reference set, {label_name} is inline")
            label_tags = _get_tags_for_given_arn(frauddetector_client, label_arn)
            tag_models = get_tag_models_from_tags(label_tags)
            label_model = models.Label(Name=label_name,
                                       Tags=tag_models,
                                       Description=label.get('description', ''),
                                       Arn=label_arn,
                                       CreatedTime=label.get('createdTime', ''),
                                       LastUpdatedTime=label.get('lastUpdatedTime', ''),
                                       Inline=True)
        # remove empty description/tags
        if not label_model.Tags:
            del label_model.Tags
        if label_model.Description is None or label_model.Description == '':
            del label_model.Description
        label_models.append(label_model)
    return label_models


# EntityTypes


def _get_entity_types_and_return_entity_types_model(frauddetector_client,
                                                    entity_type_names: List[str],
                                                    reference_entity_type_names: set
                                                    ) -> List[models.EntityType]:
    entity_type_models = []
    for entity_type_name in entity_type_names:
        get_entity_types_worked, get_entity_types_response = \
            validation_helpers.check_if_get_entity_types_succeeds(frauddetector_client, entity_type_name)
        if not get_entity_types_worked:
            raise RuntimeError(f"Error! Expected an existing get entity type, "
                               f"but entity type did not exist! entity type {entity_type_name}")
        entity_type = get_entity_types_response.get('entityTypes')[0]
        entity_type_arn = entity_type.get('arn', '')
        LOG.debug(f"checking if {entity_type_name} is in {reference_entity_type_names}")
        if entity_type_name in reference_entity_type_names:
            LOG.debug(f"in reference set, {entity_type_name} is not inline")
            entity_type_model = models.EntityType(Arn=entity_type_arn,
                                                  Name=entity_type_name,
                                                  Tags=None,
                                                  Description=None,
                                                  CreatedTime=None,
                                                  LastUpdatedTime=None,
                                                  Inline=False)
        else:
            LOG.debug(f"not in reference set, {entity_type_name} is inline")
            entity_type_tags = _get_tags_for_given_arn(frauddetector_client, entity_type.get('arn', ''))
            tag_models = get_tag_models_from_tags(entity_type_tags)
            entity_type_model = models.EntityType(Name=entity_type_name,
                                                  Tags=tag_models,
                                                  Description=entity_type.get('description', ''),
                                                  Arn=entity_type_arn,
                                                  CreatedTime=entity_type.get('createdTime', ''),
                                                  LastUpdatedTime=entity_type.get('lastUpdatedTime', ''),
                                                  Inline=True)
        # remove empty description/tags
        if not entity_type_model.Tags:
            del entity_type_model.Tags
        if entity_type_model.Description is None or entity_type_model.Description == '':
            del entity_type_model.Description
        entity_type_models.append(entity_type_model)
    return entity_type_models


# Referenced/Inline Resources


def get_referenced_resources(event_type_model: models.ResourceModel) -> dict:
    referenced_resources = {
        'event_variables': set(),
        'labels': set(),
        'entity_types': set(),
    }
    if not event_type_model:
        return referenced_resources
    LOG.debug(f"building referenced resources for event type model model: {event_type_model.Name}")
    referenced_resources['event_variables'] = {ev.Name for ev in event_type_model.EventVariables if not ev.Inline}
    referenced_resources['labels'] = {label.Name for label in event_type_model.Labels if not label.Inline}
    referenced_resources['entity_types'] = {et.Name for et in event_type_model.EntityTypes if not et.Inline}
    LOG.debug(f"returning referenced resources: {referenced_resources}")
    return referenced_resources


def get_inline_resources(event_type_model: models.ResourceModel) -> dict:
    inline_resources = {
        'event_variables': set(),
        'labels': set(),
        'entity_types': set(),
    }
    if not event_type_model:
        return inline_resources
    LOG.debug(f"building inline resources for event type model model: {event_type_model.Name}")
    inline_resources['event_variables'] = {ev.Name for ev in event_type_model.EventVariables if ev.Inline}
    inline_resources['labels'] = {label.Name for label in event_type_model.Labels if label.Inline}
    inline_resources['entity_types'] = {et.Name for et in event_type_model.EntityTypes if et.Inline}
    LOG.debug(f"returning inline resources: {inline_resources}")
    return inline_resources
