from typing import List, Optional, Set
from cloudformation_cli_python_lib import (
    exceptions,
)

from .. import models
from . import api_helpers, validation_helpers, util

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


# Tags


def get_tags_from_tag_models(
    tag_models: Optional[List[models.Tag]],
) -> Optional[List[dict]]:
    # boto3 afd client doesn't know about the 'Tags' class that cfn creates
    if tag_models is None:
        return None
    return [{"key": tag.Key, "value": tag.Value} for tag in tag_models]


def get_tag_models_from_tags(tags: Optional[List[dict]]) -> Optional[List[models.Tag]]:
    # we need to translate our afd tags back to a list of cfn Tag
    if tags is None:
        return None
    return [models.Tag(Key=tag.get("key", ""), Value=tag.get("value", "")) for tag in tags]


def _get_tags_for_given_arn(frauddetector_client, arn):
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, arn)
    return list_tags_response.get("tags", [])


# Detectors


def put_detector_for_model(frauddetector_client, model: models.ResourceModel):
    if not model.EventType.Name:
        model.EventType.Name = util.extract_name_from_arn(model.EventType.Arn)
    tags = get_tags_from_tag_models(model.Tags)
    api_helpers.call_put_detector(
        frauddetector_client=frauddetector_client,
        detector_id=model.DetectorId,
        detector_event_type_name=model.EventType.Name,
        detector_tags=tags,
        detector_description=model.Description,
    )


def get_model_for_detector(frauddetector_client, detector, model: models.ResourceModel):
    # build model from detector
    detector_id = detector.get("detectorId", "")
    detector_arn = detector.get("arn", "")
    referenced_resources = get_referenced_resources_for_detector(model)
    model_to_return = models.ResourceModel(
        DetectorId=detector_id,
        Arn=detector_arn,
        CreatedTime=detector.get("createdTime", ""),
        LastUpdatedTime=detector.get("lastUpdatedTime", ""),
        Description=detector.get("description", ""),
        EventType=None,
        DetectorVersionId=None,
        DetectorVersionStatus=None,
        RuleExecutionMode=None,
        Rules=[],
        Tags=None,
        AssociatedModels=None,
    )

    # get event type model
    event_type_model = get_event_type_and_return_event_type_model(frauddetector_client, model.EventType)
    model_to_return.EventType = event_type_model

    # get latest detector version info to attach to model
    if model.DetectorVersionId:
        desired_detector_version = api_helpers.call_get_detector_version(
            frauddetector_client, model.DetectorId, model.DetectorVersionId
        )
    else:
        describe_detectors_response = api_helpers.call_describe_detector(frauddetector_client, detector_id)
        detector_version_summaries = describe_detectors_response.get("detectorVersionSummaries", [])
        max_version_id = max(
            {int(dv_summary.get("detectorVersionId", "-1")) for dv_summary in detector_version_summaries}
        )
        desired_detector_version = api_helpers.call_get_detector_version(
            frauddetector_client, model.DetectorId, str(max_version_id)
        )
    model_to_return.DetectorVersionId = desired_detector_version.get("detectorVersionId", "-1")
    model_to_return.DetectorVersionStatus = desired_detector_version.get("status", "")
    model_to_return.RuleExecutionMode = desired_detector_version.get("ruleExecutionMode", "")

    associated_models: List[models.Model] = []
    model_endpoints: List[str] = desired_detector_version.get("externalModelEndpoints", [])
    for model_endpoint in model_endpoints:
        get_external_models_response = api_helpers.call_get_external_models(frauddetector_client, model_endpoint)
        external_models = get_external_models_response.get("externalModels", [])
        if not external_models:
            # we should never see this block get executed
            raise exceptions.NotFound("associatedModel", model_endpoint)
        associated_models.append(models.Model(Arn=external_models[0].get("arn", "not/found")))

    model_versions: List[dict] = desired_detector_version.get("modelVersions", [])
    for model_version in model_versions:
        associated_models.append(models.Model(Arn=model_version["arn"]))

    model_to_return.AssociatedModels = associated_models

    # get rule models to attach
    referenced_outcome_names = referenced_resources.get("rule_outcomes")
    for rule in desired_detector_version.get("rules", []):
        rule_detector_id = rule.get("detectorId", "")
        rule_id = rule.get("ruleId", "")
        rule_version = rule.get("ruleVersion", "-1")
        rule_to_append = get_rule_and_return_rule_model(
            frauddetector_client,
            rule_detector_id,
            rule_id,
            rule_version,
            referenced_outcome_names,
        )
        model_to_return.Rules.append(rule_to_append)

    # get tags
    detector_tags = _get_tags_for_given_arn(frauddetector_client, detector_arn)
    # TODO: reorder tags to the same order as the input model to work around contract test bug?
    model_to_return.Tags = get_tag_models_from_tags(detector_tags)

    return model_to_return


# Rules


def create_rule_for_rule_model(
    frauddetector_client, rule_model: models.Rule, detector_model: models.ResourceModel
) -> dict:
    rule_tags = get_tags_from_tag_models(rule_model.Tags)

    def get_outcome_name(outcome: models.Outcome):
        if outcome.Name:
            return outcome.Name
        return util.extract_name_from_arn(outcome.Arn)

    outcome_names = [get_outcome_name(outcome_model) for outcome_model in rule_model.Outcomes]
    create_rule_response = api_helpers.call_create_rule(
        frauddetector_client=frauddetector_client,
        rule_id=rule_model.RuleId,
        detector_id=detector_model.DetectorId,
        rule_expression=rule_model.Expression,
        rule_language=rule_model.Language,
        rule_outcomes=outcome_names,
        rule_description=rule_model.Description,
        rule_tags=rule_tags,
    )
    return create_rule_response.get("rule")


def get_rule_and_return_rule_model(
    frauddetector_client,
    detector_id: str,
    rule_id: str,
    rule_version: str,
    referenced_outcomes: set,
) -> models.Rule:
    get_rules_response = api_helpers.call_get_rules(
        frauddetector_client=frauddetector_client,
        detector_id=detector_id,
        rule_id=rule_id,
        rule_version=rule_version,
    )
    rule_details = get_rules_response.get("ruleDetails")
    if len(rule_details) != 1:
        raise exceptions.NotFound("ruleId:ruleVersion", f"{rule_id}:{rule_version}")
    rule_detail = rule_details[0]
    rule_arn = rule_detail.get("arn", "")
    rule_outcome_names = rule_detail.get("outcomes", "")
    model_to_return = models.Rule(
        Arn=rule_arn,
        CreatedTime=rule_detail.get("createdTime", ""),
        Description=rule_detail.get("description", ""),
        DetectorId=rule_detail.get("detectorId", ""),
        Expression=rule_detail.get("expression", ""),
        Language=rule_detail.get("language", ""),
        LastUpdatedTime=rule_detail.get("lastUpdatedTime", ""),
        Outcomes=[],
        RuleId=rule_detail.get("ruleId", ""),
        RuleVersion=rule_detail.get("ruleVersion", ""),
        Tags=None,
    )

    # attach tag models
    rule_tags = _get_tags_for_given_arn(frauddetector_client, rule_arn)
    model_to_return.Tags = get_tag_models_from_tags(rule_tags)

    # attach outcome models
    model_to_return.Outcomes = get_outcomes_model_for_given_outcome_names(
        frauddetector_client=frauddetector_client,
        outcome_names=rule_outcome_names,
        reference_outcome_names=referenced_outcomes,
    )
    return model_to_return


# EventTypes


def put_event_type_for_event_type_model(frauddetector_client, event_type_model: models.EventType):
    # use dependency names directly if defined Inline, otherwise extract name from arn for each
    entity_type_names = [
        [util.extract_name_from_arn(entity_type.Arn), entity_type.Name][entity_type.Inline]
        for entity_type in event_type_model.EntityTypes
    ]
    event_variable_names = [
        [util.extract_name_from_arn(event_variable.Arn), event_variable.Name][event_variable.Inline]
        for event_variable in event_type_model.EventVariables
    ]
    label_names = [
        [util.extract_name_from_arn(label.Arn), label.Name][label.Inline] for label in event_type_model.Labels
    ]
    event_type_tags = get_tags_from_tag_models(event_type_model.Tags)

    # call put event type
    api_helpers.call_put_event_type(
        frauddetector_client=frauddetector_client,
        event_type_name=event_type_model.Name,
        entity_type_names=entity_type_names,
        event_variable_names=event_variable_names,
        label_names=label_names,
        event_type_description=event_type_model.Description,
        event_type_tags=event_type_tags,
    )


def get_event_type_and_return_event_type_model(
    frauddetector_client, event_type_model: models.EventType
) -> models.EventType:
    event_type_name = event_type_model.Name
    try:
        get_event_types_response = api_helpers.call_get_event_types(frauddetector_client, event_type_name)
        event_types = get_event_types_response.get("eventTypes", [])
        if len(event_types) != 1:
            # if get event types worked but did not return any event types, we have major problems
            error_msg = f"get_event_types for {event_type_name} worked but did not return any event types!"
            LOG.error(error_msg)
            raise exceptions.NotFound("event_type", event_type_name)
        event_type = event_types[0]
        if not event_type_model.Inline:
            LOG.debug(f"{event_type_name} is not inline")
            return models.EventType(
                Name=event_type.get("name", ""),
                Arn=event_type.get("arn", ""),
                Tags=None,
                Description=None,
                EventVariables=None,
                Labels=None,
                EntityTypes=None,
                CreatedTime=None,
                LastUpdatedTime=None,
                Inline=False,
            )
        else:
            LOG.debug(f"{event_type_name} is inline")
            referenced_resources = get_referenced_resources_for_event_type(event_type_model)
            return get_model_for_inline_event_type(frauddetector_client, event_type, referenced_resources)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an event type: {e}")


def get_model_for_inline_event_type(frauddetector_client, event_type, referenced_resources: dict):
    # build model from event type
    model = models.EventType(
        Name=event_type.get("name", ""),
        Tags=[],
        Description=event_type.get("description", ""),
        EventVariables=[],
        Labels=[],
        EntityTypes=[],
        Arn=event_type.get("arn", ""),
        CreatedTime=event_type.get("createdTime", ""),
        LastUpdatedTime=event_type.get("lastUpdatedTime", ""),
        Inline=True,
    )

    # attach Tags
    event_type_arn = event_type.get("arn", "")
    event_type_tags = _get_tags_for_given_arn(frauddetector_client, event_type_arn)
    # TODO: reorder tags to the same order as the input model to work around contract test bug?
    model.Tags = get_tag_models_from_tags(event_type_tags)

    # attach EventVariables
    event_variables = event_type.get("eventVariables", [])
    model.EventVariables = _get_variables_and_return_event_variables_model(
        frauddetector_client, event_variables, referenced_resources["event_variables"]
    )

    # attach Labels
    event_type_labels = event_type.get("labels", [])
    model.Labels = _get_labels_and_return_labels_model(
        frauddetector_client, event_type_labels, referenced_resources["labels"]
    )

    # attach EntityTypes
    event_type_entity_types = event_type.get("entityTypes", [])
    model.EntityTypes = _get_entity_types_and_return_entity_types_model(
        frauddetector_client,
        event_type_entity_types,
        referenced_resources["entity_types"],
    )

    # remove empty description/tags
    if not model.Tags:
        del model.Tags
    if model.Description is None or model.Description == "":
        del model.Description

    # return model
    return model


# Outcomes


def get_outcomes_model_for_given_outcome_names(frauddetector_client, outcome_names, reference_outcome_names):
    outcome_models = []
    for outcome_name in outcome_names:
        get_outcomes_response = api_helpers.call_get_outcomes(frauddetector_client, outcome_name)
        outcomes = get_outcomes_response.get("outcomes", [])
        if len(outcomes) != 1:
            raise RuntimeError(
                f"Error! Expected an existing outcome, but outcome did not exist! outcome {outcome_name}"
            )
        outcome = outcomes[0]
        outcome_arn = outcome.get("arn", "")
        LOG.debug(f"checking if outcome {outcome_name} is in {reference_outcome_names}")
        if outcome_name in reference_outcome_names:
            LOG.debug(f"outcome in reference set, {outcome_name} is not defined inline")
            outcome_model = models.Outcome(
                Name=outcome_name,
                Arn=outcome_arn,
                Tags=None,
                Description=None,
                CreatedTime=None,
                LastUpdatedTime=None,
                Inline=False,
            )
        else:
            LOG.debug(f"outcome not in reference set, {outcome_name} is inline")
            outcome_tags = _get_tags_for_given_arn(frauddetector_client, outcome_arn)
            tag_models = get_tag_models_from_tags(outcome_tags)
            outcome_model = models.Outcome(
                Name=outcome_name,
                Tags=tag_models,
                Description=outcome.get("description", ""),
                Arn=outcome_arn,
                CreatedTime=outcome.get("createdTime", ""),
                LastUpdatedTime=outcome.get("lastUpdatedTime", ""),
                Inline=True,
            )
        # remove empty description/tags
        LOG.debug(f"removing empty descriptions/tags from outcome model: {outcome_model}")
        if not outcome_model.Tags:
            del outcome_model.Tags
        if outcome_model.Description is None or outcome_model.Description == "":
            del outcome_model.Description
        outcome_models.append(outcome_model)
    return outcome_models


# EventVariables


def _get_variables_and_return_event_variables_model(
    frauddetector_client, variable_names, reference_variable_names: set
):
    collected_variables = []
    for variable_name in variable_names:
        # use singular get_variables to preserve order (transient contract test bug workaround)
        get_variables_response = api_helpers.call_get_variables(frauddetector_client, variable_name)
        collected_variables.extend(get_variables_response.get("variables", []))
    return _get_event_variables_model_for_given_variables(
        frauddetector_client, collected_variables, reference_variable_names
    )


def _get_event_variables_model_for_given_variables(frauddetector_client, variables, reference_variable_names: set):
    variable_models = []
    for variable in variables:
        variable_tags = _get_tags_for_given_arn(frauddetector_client, variable.get("arn", ""))
        tag_models = get_tag_models_from_tags(variable_tags)
        variable_name = util.extract_name_from_arn(variable.get("arn", ""))
        LOG.debug(f"checking if {variable_name} is in {reference_variable_names}")
        if variable_name in reference_variable_names:
            LOG.debug(f"in reference set, {variable_name} is not inline")
            variable_model = models.EventVariable(
                Arn=variable.get("arn", ""),
                Name=variable_name,
                Tags=None,
                Description=None,
                DataType=None,
                DataSource=None,
                DefaultValue=None,
                VariableType=None,
                CreatedTime=None,
                LastUpdatedTime=None,
                Inline=False,
            )
        else:
            LOG.debug(f"not in reference set, {variable_name} is inline")
            variable_model = models.EventVariable(
                Name=variable.get("name", ""),
                Tags=tag_models,
                Description=variable.get("description", ""),
                DataType=variable.get("dataType", ""),
                DataSource=variable.get("dataSource", ""),
                DefaultValue=variable.get("defaultValue", ""),
                VariableType=variable.get("variableType", ""),
                Arn=variable.get("arn", ""),
                CreatedTime=variable.get("createdTime", ""),
                LastUpdatedTime=variable.get("lastUpdatedTime", ""),
                Inline=True,
            )
        # remove empty description/tags
        if not variable_model.Tags:
            del variable_model.Tags
        if variable_model.Description is None or variable_model.Description == "":
            del variable_model.Description
        variable_models.append(variable_model)
    return variable_models


# Labels


def _get_labels_and_return_labels_model(frauddetector_client, label_names, reference_label_names: set):
    label_models = []
    for label_name in label_names:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name)
        labels = get_labels_response.get("labels", [])
        if not labels:
            raise RuntimeError(f"Error! Expected an existing label, but label did not exist! label name {label_name}")
        label = labels[0]
        label_arn = label.get("arn", "")
        LOG.debug(f"checking if {label_name} is in {reference_label_names}")
        if label_name in reference_label_names:
            LOG.debug(f"in reference set, {label_name} is not inline")
            label_model = models.Label(
                Arn=label_arn,
                Name=label_name,
                Tags=None,
                Description=None,
                CreatedTime=None,
                LastUpdatedTime=None,
                Inline=False,
            )
        else:
            LOG.debug(f"not in reference set, {label_name} is inline")
            label_tags = _get_tags_for_given_arn(frauddetector_client, label_arn)
            tag_models = get_tag_models_from_tags(label_tags)
            label_model = models.Label(
                Name=label_name,
                Tags=tag_models,
                Description=label.get("description", ""),
                Arn=label_arn,
                CreatedTime=label.get("createdTime", ""),
                LastUpdatedTime=label.get("lastUpdatedTime", ""),
                Inline=True,
            )
        # remove empty description/tags
        if not label_model.Tags:
            del label_model.Tags
        if label_model.Description is None or label_model.Description == "":
            del label_model.Description
        label_models.append(label_model)
    return label_models


# EntityTypes


def _get_entity_types_and_return_entity_types_model(
    frauddetector_client, entity_type_names: List[str], reference_entity_type_names: set
) -> List[models.EntityType]:
    entity_type_models = []
    for entity_type_name in entity_type_names:
        (
            get_entity_types_worked,
            get_entity_types_response,
        ) = validation_helpers.check_if_get_entity_types_succeeds(frauddetector_client, entity_type_name)
        if not get_entity_types_worked:
            raise RuntimeError(
                f"Error! Expected an existing get entity type, "
                f"but entity type did not exist! entity type {entity_type_name}"
            )
        entity_type = get_entity_types_response.get("entityTypes")[0]
        entity_type_arn = entity_type.get("arn", "")
        LOG.debug(f"checking if {entity_type_name} is in {reference_entity_type_names}")
        if entity_type_name in reference_entity_type_names:
            LOG.debug(f"in reference set, {entity_type_name} is not inline")
            entity_type_model = models.EntityType(
                Arn=entity_type_arn,
                Name=entity_type_name,
                Tags=None,
                Description=None,
                CreatedTime=None,
                LastUpdatedTime=None,
                Inline=False,
            )
        else:
            LOG.debug(f"not in reference set, {entity_type_name} is inline")
            entity_type_tags = _get_tags_for_given_arn(frauddetector_client, entity_type.get("arn", ""))
            tag_models = get_tag_models_from_tags(entity_type_tags)
            entity_type_model = models.EntityType(
                Name=entity_type_name,
                Tags=tag_models,
                Description=entity_type.get("description", ""),
                Arn=entity_type_arn,
                CreatedTime=entity_type.get("createdTime", ""),
                LastUpdatedTime=entity_type.get("lastUpdatedTime", ""),
                Inline=True,
            )
        # remove empty description/tags
        if not entity_type_model.Tags:
            del entity_type_model.Tags
        if entity_type_model.Description is None or entity_type_model.Description == "":
            del entity_type_model.Description
        entity_type_models.append(entity_type_model)
    return entity_type_models


# External Models for Detector


def get_external_model_arns_from_model(model: models.ResourceModel) -> Set[str]:
    if model.AssociatedModels is None:
        return set()
    return {m.Arn for m in model.AssociatedModels if util.is_external_model_arn(m.Arn)}


def get_external_model_endpoints_from_model(model: models.ResourceModel) -> List[str]:
    if model.AssociatedModels is None:
        return []
    return [util.extract_name_from_arn(m.Arn) for m in model.AssociatedModels if util.is_external_model_arn(m.Arn)]


# Model Versions for Detector


def get_model_versions_from_model(model: models.ResourceModel) -> List[dict]:
    if model.AssociatedModels is None:
        return []

    model_versions = []

    for m in model.AssociatedModels:
        model_id, model_type, model_version_number = util.get_model_version_details_from_arn(m.Arn)
        model_versions.append(
            {"modelId": model_id, "modelType": model_type, "modelVersionNumber": model_version_number}
        )

    return model_versions


# Referenced/Inline Resources


def get_referenced_resources_for_event_type(event_type_model: models.EventType) -> dict:
    referenced_resources = {
        "event_variables": set(),
        "labels": set(),
        "entity_types": set(),
    }
    if not event_type_model:
        return referenced_resources
    LOG.debug(f"building referenced resources for event type model: {event_type_model.Name}")
    referenced_resources["event_variables"] = {ev.Name for ev in event_type_model.EventVariables if not ev.Inline}
    referenced_resources["labels"] = {label.Name for label in event_type_model.Labels if not label.Inline}
    referenced_resources["entity_types"] = {et.Name for et in event_type_model.EntityTypes if not et.Inline}
    LOG.debug(f"returning referenced resources: {referenced_resources}")
    return referenced_resources


def get_referenced_resources_for_detector(detector_model: models.ResourceModel) -> dict:
    referenced_resources = {
        "rule_outcomes": set(),
        "event_type": set(),
    }
    if not detector_model:
        return referenced_resources
    LOG.debug(f"building referenced resources for detector model: {detector_model.DetectorId}")
    for rule_model in detector_model.Rules:
        for outcome_model in rule_model.Outcomes:
            if not outcome_model.Inline:
                outcome_name = [
                    util.extract_name_from_arn(outcome_model.Arn),
                    outcome_model.Name,
                ][outcome_model.Name is not None]
                referenced_resources["rule_outcomes"].add(outcome_name)
    if not detector_model.EventType.Inline:
        referenced_resources["event_type"].add(util.extract_name_from_arn(detector_model.EventType.Arn))
    LOG.debug(f"returning referenced resources: {referenced_resources}")
    return referenced_resources


def get_inline_resources_for_event_type(event_type_model: models.EventType) -> dict:
    inline_resources = {
        "event_variables": set(),
        "labels": set(),
        "entity_types": set(),
    }
    if not event_type_model:
        return inline_resources
    LOG.debug(f"building inline resources for event type model: {event_type_model.Name}")
    inline_resources["event_variables"] = {ev.Name for ev in event_type_model.EventVariables if ev.Inline}
    inline_resources["labels"] = {label.Name for label in event_type_model.Labels if label.Inline}
    inline_resources["entity_types"] = {et.Name for et in event_type_model.EntityTypes if et.Inline}
    LOG.debug(f"returning inline resources: {inline_resources}")
    return inline_resources
