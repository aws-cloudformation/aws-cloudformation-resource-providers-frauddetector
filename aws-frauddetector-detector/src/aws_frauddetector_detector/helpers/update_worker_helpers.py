import logging
from typing import Tuple, Set

from cloudformation_cli_python_lib import (
    exceptions,
)

from . import validation_helpers, api_helpers, common_helpers, model_helpers, util
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


DRAFT_STATUS = "DRAFT"


def validate_dependencies_for_detector_update(
    afd_client, model: models.ResourceModel, previous_model: models.ResourceModel
):
    # TODO: revisit  this validation when/if we support in-place teardown
    # For now, throw bad request for unsupported event type update, and validate external models + model versions
    # (Other updates that would require teardown will throw exception and trigger rollback)
    if model.EventType.Name != previous_model.EventType.Name:
        raise exceptions.InvalidRequest(f"Error: EventType.Name update is not allowed")
    if model.EventType.Inline != previous_model.EventType.Inline:
        raise exceptions.InvalidRequest(f"Error: EventType.Inline update is not allowed")
    if not model.EventType.Inline:
        event_type_name = util.extract_name_from_arn(model.EventType.Arn)
        (
            get_event_types_succeeded,
            _,
        ) = validation_helpers.check_if_get_event_types_succeeds(afd_client, event_type_name)
        if not get_event_types_succeeded:
            raise exceptions.NotFound("detector.EventType", event_type_name)
    validation_helpers.validate_external_models_for_detector_model(afd_client, model)
    validation_helpers.validate_model_versions_for_detector_model(afd_client, model)


def update_rules_and_inline_outcomes_for_detector_update(
    afd_client, model: models.ResourceModel, previous_model: models.ResourceModel
) -> (Set[Tuple[str, str]], Set[str]):
    # build list of kept rules, unused rules & new rules
    previous_rules_by_rule_id = {r.RuleId: r for r in previous_model.Rules}
    current_rules_by_rule_id = {r.RuleId: r for r in model.Rules}

    # get list of outcomes and rule versions to delete
    (unused_rule_versions, unused_inline_outcomes,) = _get_unused_rule_versions_and_inline_outcomes(
        afd_client=afd_client,
        detector_id=model.DetectorId,
        previous_rules_by_rule_id=previous_rules_by_rule_id,
        current_rules_by_rule_id=current_rules_by_rule_id,
    )

    # create new inline outcomes and rules
    new_rule_versions_by_rule_id = _create_new_inline_outcomes_and_rules(
        afd_client=afd_client,
        detector_id=model.DetectorId,
        previous_rules_by_rule_id=previous_rules_by_rule_id,
        current_rules_by_rule_id=current_rules_by_rule_id,
    )

    # update persisting rules and rule artifacts (inline outcomes, rule versions)
    (
        rule_versions_to_delete,
        inline_outcomes_to_delete,
        persisting_rule_versions_by_rule_id,
    ) = _update_persisting_rules(
        afd_client=afd_client,
        detector_id=model.DetectorId,
        previous_rules_by_rule_id=previous_rules_by_rule_id,
        current_rules_by_rule_id=current_rules_by_rule_id,
    )

    # update model to include rule version for rules
    LOG.debug(f"updating rule models: {model.Rules} with rule versions by rule id {new_rule_versions_by_rule_id}")
    new_rule_versions_by_rule_id.update(persisting_rule_versions_by_rule_id)
    for rule_model in model.Rules:
        if rule_model.RuleId in new_rule_versions_by_rule_id:
            rule_model.RuleVersion = new_rule_versions_by_rule_id.get(rule_model.RuleId)
    LOG.debug(f"updated rule models: {model.Rules}")

    # update unused rule versions and inline outcomes from persisting rules
    unused_rule_versions.update(rule_versions_to_delete)
    unused_inline_outcomes.update(inline_outcomes_to_delete)

    # return rules and outcomes to delete (need to delete after updating detector version)
    return unused_rule_versions, unused_inline_outcomes


def update_detector_version_for_detector_update(
    afd_client, model: models.ResourceModel, previous_model: models.ResourceModel
) -> Set[Tuple[str, str]]:
    # update detector version - create if previous is not draft
    # update tags
    # return set of unused detector versions (tuple: detector_id, detector_version_id)
    # TODO: update this for models + external models when we support them in CFN
    desired_rules = []
    for rule_model in model.Rules:
        rule_dict = {
            "detectorId": model.DetectorId,
            "ruleId": rule_model.RuleId,
            "ruleVersion": rule_model.RuleVersion,  # rule version needs to be set before this
        }
        desired_rules.append(rule_dict)
    if previous_model.DetectorVersionStatus != DRAFT_STATUS:
        LOG.info("previous detector version status was not DRAFT. creating a new detector version")
        api_helpers.call_create_detector_version(
            frauddetector_client=afd_client,
            detector_id=model.DetectorId,
            rules=desired_rules,
            rule_execution_mode=model.RuleExecutionMode,
            model_versions=[],
            external_model_endpoints=[],
            detector_version_description=model.Description,
            detector_version_tags=model_helpers.get_tags_from_tag_models(model.Tags),
        )
    else:
        LOG.info("previous detector version status was DRAFT. updating detector version in place")
        api_helpers.call_update_detector_version(
            frauddetector_client=afd_client,
            detector_id=model.DetectorId,
            detector_version_id=model.DetectorVersionId,
            rules=desired_rules,
            rule_execution_mode=model.RuleExecutionMode,
            model_versions=[],
            external_model_endpoints=[],
            detector_version_description=model.Description,
        )
    # get arn of max version detector version in order to update tags and model
    describe_detector_response = api_helpers.call_describe_detector(afd_client, model.DetectorId)
    dv_summaries = describe_detector_response.get("detectorVersionSummaries", [])
    dv_ids = [summary.get("detectorVersionId", "-1") for summary in dv_summaries]
    max_dv_id = str(max([int(dv_id) for dv_id in dv_ids]))
    model.DetectorVersionId = max_dv_id
    if previous_model.DetectorVersionStatus == DRAFT_STATUS:
        LOG.info("previous detector version status was DRAFT. updating tags separately")
        # update dv does not update tags, so update tags in this case
        get_dv_response = api_helpers.call_get_detector_version(
            frauddetector_client=afd_client,
            detector_id=model.DetectorId,
            detector_version_id=max_dv_id,
        )
        latest_dv_arn = get_dv_response.get("arn", None)
        common_helpers.update_tags(
            frauddetector_client=afd_client,
            afd_resource_arn=latest_dv_arn,
            new_tags=model.Tags,
        )

    if model.DetectorVersionStatus != DRAFT_STATUS:
        LOG.info(f"desired status is not DRAFT. updating detector version status: {model.DetectorVersionStatus}")
        api_helpers.call_update_detector_version_status(
            frauddetector_client=afd_client,
            detector_id=model.DetectorId,
            detector_version_id=max_dv_id,
            status=model.DetectorVersionStatus,
        )

    dvs_to_delete = set()
    new_describe_detector_response = api_helpers.call_describe_detector(afd_client, model.DetectorId)
    updated_dv_summaries = new_describe_detector_response.get("detectorVersionSummaries", [])
    LOG.info(f"updated detector version summaries: {updated_dv_summaries}")
    for summary in updated_dv_summaries:
        dv_id = summary.get("detectorVersionId", "-1")
        dv_status = summary.get("status", "ACTIVE")
        if dv_id == max_dv_id or dv_status == "ACTIVE":
            continue
        dvs_to_delete.add((model.DetectorId, dv_id))

    LOG.info(f"detector versions to delete: {dvs_to_delete}")
    return dvs_to_delete


def delete_unused_detector_versions_for_detector_update(afd_client, unused_detector_versions: Set[Tuple[str, str]]):
    for detector_id, detector_version_id in unused_detector_versions:
        api_helpers.call_delete_detector_version(
            frauddetector_client=afd_client,
            detector_id=detector_id,
            detector_version_id=detector_version_id,
        )


def delete_unused_rules_for_detector_update(afd_client, detector_id: str, unused_rule_versions: Set[Tuple[str, str]]):
    # For now, just catch conditional check failed exception, which means the rule is still used.
    # We will follow up with a more optimal approach (and avoid the try/catch)
    for unused_rule_id, unused_rule_version in unused_rule_versions:
        try:
            api_helpers.call_delete_rule(
                frauddetector_client=afd_client,
                detector_id=detector_id,
                rule_id=unused_rule_id,
                rule_version=unused_rule_version,
            )
        except afd_client.exceptions.ConflictException as conflictException:
            LOG.warning(
                f"Conflict exception when deleting rule! Continuing without failure. "
                f"This is likely from a rule being present in an active detector version. "
                f"This can happen when transitioning from ACTIVE -> DRAFT, and keeping the ACTIVE version. "
                f"Exception: {conflictException}"
            )


def delete_unused_inline_outcomes_for_detector_update(afd_client, unused_inline_outcome_names: Set[str]):
    for unused_outcome_name in unused_inline_outcome_names:
        api_helpers.call_delete_outcome(frauddetector_client=afd_client, outcome_name=unused_outcome_name)


def validate_dependencies_for_inline_event_type_update(
    afd_client,
    event_type_model: models.EventType,
    previous_event_type_model: models.EventType,
):
    # TODO: revisit  this validation when/if we support in-place teardown
    # is_teardown_required = _determine_if_teardown_is_required(afd_client, model, previous_model)
    # if is_teardown_required and not model.AllowTeardown:
    #     raise RuntimeError(TEARDOWN_CONFLICT_MESSAGE)
    _validate_event_variables_for_event_type_update(afd_client, event_type_model, previous_event_type_model)
    _validate_entity_types_for_event_type_update(afd_client, event_type_model, previous_event_type_model)
    _validate_labels_for_event_type_update(afd_client, event_type_model, previous_event_type_model)


def update_inline_event_type(
    afd_client,
    event_type_model: models.EventType,
    previous_event_type_model: models.EventType,
):
    # NOTE: we've already done validation in `validate_dependencies_for_detector_update`
    #       In the future, we might want to move some event type specific validation here instead.
    model_helpers.put_event_type_for_event_type_model(
        frauddetector_client=afd_client, event_type_model=event_type_model
    )

    # if there is no difference in tags, we're done
    if event_type_model.Tags == previous_event_type_model.Tags:
        return

    # update tags separately, for which we need Arn. get the eventtype we just updated to get arn
    (get_event_types_worked, get_event_types_response,) = validation_helpers.check_if_get_event_types_succeeds(
        frauddetector_client=afd_client, event_type_to_check=event_type_model.Name
    )

    # this should never happen, but throw internal failure if it does
    if not get_event_types_worked:
        error_message = f"Updating inline event type {event_type_model.Name}, but no event type exists!!!"
        LOG.error(error_message)
        raise exceptions.InternalFailure(error_message)

    # get arn and update tags
    event_type_arn = get_event_types_response.get("eventTypes")[0].get("arn", None)
    common_helpers.update_tags(
        frauddetector_client=afd_client,
        afd_resource_arn=event_type_arn,
        new_tags=event_type_model.Tags,
    )


def _get_unused_rule_versions_and_inline_outcomes(
    afd_client,
    detector_id: str,
    previous_rules_by_rule_id: dict,
    current_rules_by_rule_id: dict,
) -> (Set[str], Set[str]):
    unused_rule_versions = set()
    unused_inline_outcomes = set()
    unused_rule_ids = [
        rule_id for rule_id in previous_rules_by_rule_id.keys() if rule_id not in current_rules_by_rule_id
    ]

    # build list of outcomes and rule versions to delete
    for unused_rule_id in unused_rule_ids:
        unused_rule_model: models.Rule = previous_rules_by_rule_id[unused_rule_id]

        # outcomes to delete
        outcomes_to_delete = {outcome.Name for outcome in unused_rule_model.Outcomes if outcome.Inline}
        unused_inline_outcomes.update(outcomes_to_delete)

        # rule versions to delete
        get_rules_response = api_helpers.call_get_rules(
            frauddetector_client=afd_client,
            detector_id=detector_id,
            rule_id=unused_rule_id,
        )
        rule_details = get_rules_response.get("ruleDetails", [])
        rule_versions_to_delete = {(rd.get("ruleId", None), rd.get("ruleVersion", None)) for rd in rule_details}
        unused_rule_versions.update(rule_versions_to_delete)
    return unused_rule_versions, unused_inline_outcomes


def _create_new_inline_outcomes_and_rules(
    afd_client,
    detector_id: str,
    previous_rules_by_rule_id: dict,
    current_rules_by_rule_id: dict,
):
    # build list of new rules (and new inline outcomes) to create
    outcomes_to_create = {}
    rules_to_create = {}
    new_rule_ids = [rule_id for rule_id in current_rules_by_rule_id.keys() if rule_id not in previous_rules_by_rule_id]
    for new_rule_id in new_rule_ids:
        new_rule_model: models.Rule = current_rules_by_rule_id[new_rule_id]
        outcomes_to_create.update({outcome.Name: outcome for outcome in new_rule_model.Outcomes if outcome.Inline})
        rules_to_create.update({new_rule_model.RuleId: new_rule_model})

    # create new inline outcomes and new rules
    _create_new_inline_outcomes(afd_client, outcomes_to_create)
    return _create_new_rules(afd_client, detector_id, rules_to_create)


def _create_new_inline_outcomes(afd_client, outcomes_to_create: dict):
    for outcome_name, outcome_model in outcomes_to_create.items():
        tags = model_helpers.get_tags_from_tag_models(outcome_model.Tags)
        api_helpers.call_put_outcome(
            frauddetector_client=afd_client,
            outcome_name=outcome_name,
            outcome_tags=tags,
            outcome_description=outcome_model.Description,
        )


def _create_new_rules(afd_client, detector_id: str, rules_to_create: dict) -> dict:
    new_rule_versions_by_rule_id = {}
    for rule_id, rule_model in rules_to_create.items():
        tags = model_helpers.get_tags_from_tag_models(rule_model.Tags)
        rule_outcomes = [outcome.Name for outcome in rule_model.Outcomes]
        create_rule_response = api_helpers.call_create_rule(
            frauddetector_client=afd_client,
            rule_id=rule_id,
            detector_id=detector_id,
            rule_expression=rule_model.Expression,
            rule_language=rule_model.Language,
            rule_outcomes=rule_outcomes,
            rule_description=rule_model.Description,
            rule_tags=tags,
        )
        new_rule_versions_by_rule_id[rule_id] = create_rule_response.get("rule", {}).get("ruleVersion", None)
    return new_rule_versions_by_rule_id


def _update_persisting_rules(
    afd_client,
    detector_id: str,
    previous_rules_by_rule_id: dict,
    current_rules_by_rule_id: dict,
) -> (Set[Tuple[str, str]], Set[str], dict):
    unused_rule_versions = set()
    unused_inline_outcomes = set()
    persisting_rule_versions_by_rule_id = dict()
    persisting_rule_ids = previous_rules_by_rule_id.keys() & current_rules_by_rule_id.keys()
    for persisting_rule_id in persisting_rule_ids:
        current_rule_model: models.Rule = current_rules_by_rule_id[persisting_rule_id]
        previous_rule_model: models.Rule = previous_rules_by_rule_id[persisting_rule_id]
        (
            rule_versions_to_delete,
            inline_outcomes_to_delete,
            persisting_rule_version_by_rule_id,
        ) = _update_persisting_rule(afd_client, detector_id, current_rule_model, previous_rule_model)
        unused_rule_versions.update(rule_versions_to_delete)
        unused_inline_outcomes.update(inline_outcomes_to_delete)
        persisting_rule_versions_by_rule_id.update(persisting_rule_version_by_rule_id)

    return (
        unused_rule_versions,
        unused_inline_outcomes,
        persisting_rule_versions_by_rule_id,
    )


def _update_persisting_rule(
    afd_client,
    detector_id: str,
    current_rule_model: models.Rule,
    previous_rule_model: models.Rule,
) -> (Set[Tuple[str, str]], Set[str], dict):
    # check new outcomes vs old outcomes
    previous_outcomes_by_name = {outcome.Name: outcome for outcome in previous_rule_model.Outcomes}
    current_outcomes_by_name = {outcome.Name: outcome for outcome in current_rule_model.Outcomes}
    unused_inline_outcome_names = {
        outcome_name
        for outcome_name, outcome in previous_outcomes_by_name.items()
        if outcome_name not in current_outcomes_by_name and outcome.Inline
    }
    outcomes_to_update = {
        outcome_name: outcome
        for outcome_name, outcome in current_outcomes_by_name.items()
        if outcome_name not in unused_inline_outcome_names and outcome.Inline
    }

    # new outcome model will not have Arn, as Arn is readonly for inline outcomes
    existing_outcome_models = model_helpers.get_outcomes_model_for_given_outcome_names(
        frauddetector_client=afd_client,
        outcome_names=outcomes_to_update.keys(),
        reference_outcome_names=set(),
    )

    for existing_outcome in existing_outcome_models:
        desired_outcome_model = outcomes_to_update[existing_outcome.Name]
        new_tags = model_helpers.get_tags_from_tag_models(desired_outcome_model.Tags)
        api_helpers.call_put_outcome(
            frauddetector_client=afd_client,
            outcome_name=desired_outcome_model.Name,
            outcome_description=desired_outcome_model.Description,
        )
        # use arn from existing outcome model to update tags
        common_helpers.update_tags(
            frauddetector_client=afd_client,
            afd_resource_arn=existing_outcome.Arn,
            new_tags=new_tags,
        )

    # rather than check all the differences, we can just update rule version and call it a day
    #   first, we need to get rules and grab latest version, since it's not anywhere
    get_rules_response = api_helpers.call_get_rules(
        frauddetector_client=afd_client,
        detector_id=detector_id,
        rule_id=current_rule_model.RuleId,
    )
    rule_details = get_rules_response.get("ruleDetails", [])
    rule_versions = [int(rd.get("ruleVersion", "-1")) for rd in rule_details]
    max_rule_version_string = str(max(rule_versions))

    update_rule_version_response = api_helpers.call_update_rule_version(
        frauddetector_client=afd_client,
        detector_id=detector_id,
        rule_id=current_rule_model.RuleId,
        rule_version=max_rule_version_string,
        rule_expression=current_rule_model.Expression,
        rule_language=current_rule_model.Language,
        rule_outcomes=list(current_outcomes_by_name.keys()),
        rule_description=current_rule_model.Description,
        rule_tags=model_helpers.get_tags_from_tag_models(current_rule_model.Tags),
    )

    # gather old rule versions to delete
    rule_version_to_keep = update_rule_version_response.get("rule", {}).get("ruleVersion", None)
    get_rules_response = api_helpers.call_get_rules(
        frauddetector_client=afd_client,
        detector_id=detector_id,
        rule_id=current_rule_model.RuleId,
    )
    rule_details = get_rules_response.get("ruleDetails", [])
    rule_versions_to_delete = {
        (rd.get("ruleId", None), rd.get("ruleVersion", None))
        for rd in rule_details
        if rd.get("ruleVersion", None) != rule_version_to_keep
    }

    return (
        rule_versions_to_delete,
        unused_inline_outcome_names,
        {current_rule_model.RuleId: rule_version_to_keep},
    )


def _validate_event_variables_for_event_type_update(
    afd_client,
    event_type_model: models.EventType,
    previous_event_type_model: models.EventType,
):
    previous_variables = {variable.Name: variable for variable in previous_event_type_model.EventVariables}
    new_event_variable_names = set()
    for event_variable in event_type_model.EventVariables:
        _validate_event_variable_for_event_type_update(afd_client, event_variable, previous_variables)
        new_event_variable_names.add(event_variable.Name)

    # remove previous inline variables that are no longer in the event type
    for previous_variable_name, previous_variable in previous_variables.items():
        if previous_variable_name not in new_event_variable_names and previous_variable.Inline:
            api_helpers.call_delete_variable(frauddetector_client=afd_client, variable_name=previous_variable_name)


def _validate_event_variable_for_event_type_update(afd_client, event_variable, previous_variables):
    if event_variable.Inline:
        _validate_inline_event_variable_for_event_type_update(afd_client, event_variable, previous_variables)
    else:
        _validate_referenced_event_variable_for_event_type_update(afd_client, event_variable)


def _validate_referenced_event_variable_for_event_type_update(afd_client, event_variable):
    event_variable_name = util.extract_name_from_arn(event_variable.Arn)
    get_variables_worked, _ = validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable_name)
    if not get_variables_worked:
        raise exceptions.NotFound("event_variable", event_variable.Arn)


def _validate_inline_event_variable_for_event_type_update(afd_client, event_variable, previous_variables):
    if not event_variable.Name:
        raise exceptions.InvalidRequest("Error occurred: inline event variables must include Name!")

    # TODO: update this logic if we support in-place Teardown
    #       This difference would require teardown if we were to support it

    # check for differences in dataSource or dataType
    differences = {}
    previous_variable = previous_variables.get(event_variable.Name, None)
    if previous_variable:
        differences = validation_helpers.check_variable_differences(previous_variable, event_variable)
    if differences["dataSource"] or differences["dataType"]:
        raise exceptions.InvalidRequest("Error occurred: cannot update event variable data source or data type!")

    if not previous_variable:
        # create inline variable that does not already exist
        common_helpers.create_inline_event_variable(frauddetector_client=afd_client, event_variable=event_variable)
    else:
        # get existing variable to get arn. Arn is readonly property, so it will not be attached to input model
        (
            get_variables_worked,
            get_variables_response,
        ) = validation_helpers.check_if_get_variables_succeeds(afd_client, event_variable.Name)
        if not get_variables_worked:
            raise RuntimeError(f"Previously existing event variable {event_variable.Name} no longer exists!")
        event_variable.Arn = get_variables_response.get("variables")[0].get("arn")
        # update existing inline variable
        if hasattr(event_variable, "Tags"):
            common_helpers.update_tags(
                frauddetector_client=afd_client,
                afd_resource_arn=event_variable.Arn,
                new_tags=event_variable.Tags,
            )
        var_type = [None, event_variable.VariableType][event_variable.VariableType != previous_variable.VariableType]
        api_helpers.call_update_variable(
            variable_name=event_variable.Name,
            frauddetector_client=afd_client,
            variable_default_value=event_variable.DefaultValue,
            variable_description=event_variable.Description,
            variable_type=var_type,
        )


def _validate_entity_types_for_event_type_update(
    afd_client,
    event_type_model: models.EventType,
    previous_event_type_model: models.EventType,
):
    previous_entity_types = {entity_type.Name: entity_type for entity_type in previous_event_type_model.EntityTypes}
    new_entity_type_names = set()
    for entity_type in event_type_model.EntityTypes:
        _validate_entity_type_for_event_type_update(afd_client, entity_type, previous_entity_types)
        new_entity_type_names.add(entity_type.Name)

    # remove previous inline entity types that are no longer in the event type
    for (
        previous_entity_type_name,
        previous_entity_type,
    ) in previous_entity_types.items():
        if previous_entity_type_name not in new_entity_type_names and previous_entity_type.Inline:
            api_helpers.call_delete_entity_type(
                frauddetector_client=afd_client,
                entity_type_name=previous_entity_type_name,
            )


def _validate_entity_type_for_event_type_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Inline:
        _validate_inline_entity_type_for_event_type_update(afd_client, entity_type, previous_entity_types)
    else:
        _validate_referenced_entity_type_for_event_type_update(afd_client, entity_type)


def _validate_referenced_entity_type_for_event_type_update(afd_client, entity_type):
    entity_type_name = util.extract_name_from_arn(entity_type.Arn)
    get_entity_types_worked, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type_name)
    if not get_entity_types_worked:
        raise exceptions.NotFound("entity_type", entity_type.Arn)


def _validate_inline_entity_type_for_event_type_update(afd_client, entity_type, previous_entity_types):
    if entity_type.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline entity types must include Name!")

    previous_entity_type = previous_entity_types.get(entity_type.Name, None)
    if not previous_entity_type:
        # put inline entity type that does not already exist
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
    else:
        # get existing entity type to get arn. Arn is readonly property, so it will not be attached to input model
        (
            get_entity_types_worked,
            get_entity_types_response,
        ) = validation_helpers.check_if_get_entity_types_succeeds(afd_client, entity_type.Name)
        if not get_entity_types_worked:
            raise RuntimeError(f"Previously existing entity type {entity_type.Name} no longer exists!")
        entity_type.Arn = get_entity_types_response.get("entityTypes")[0].get("arn")
        # put existing inline entity type and update tags
        common_helpers.put_inline_entity_type(frauddetector_client=afd_client, entity_type=entity_type)
        if hasattr(entity_type, "Tags"):
            common_helpers.update_tags(
                frauddetector_client=afd_client,
                afd_resource_arn=entity_type.Arn,
                new_tags=entity_type.Tags,
            )


def _validate_labels_for_event_type_update(
    afd_client,
    event_type_model: models.EventType,
    previous_event_type_model: models.EventType,
):
    previous_labels = {label.Name: label for label in previous_event_type_model.Labels}
    new_label_names = set()
    for label in event_type_model.Labels:
        _validate_label_for_event_type_update(afd_client, label, previous_labels)
        new_label_names.add(label.Name)

    # remove previous inline labels that are no longer in the event type
    for previous_label_name, previous_label in previous_labels.items():
        if previous_label_name not in new_label_names and previous_label.Inline:
            api_helpers.call_delete_label(frauddetector_client=afd_client, label_name=previous_label_name)


def _validate_label_for_event_type_update(afd_client, label, previous_labels):
    if label.Inline:
        _validate_inline_label_for_event_type_update(afd_client, label, previous_labels)
    else:
        _validate_referenced_label_for_event_type_update(afd_client, label)


def _validate_referenced_label_for_event_type_update(afd_client, label):
    label_name = util.extract_name_from_arn(label.Arn)
    get_labels_worked, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, label_name)
    if not get_labels_worked:
        raise exceptions.NotFound("label", label.Arn)


def _validate_inline_label_for_event_type_update(afd_client, label, previous_labels):
    if label.Name is None:
        raise exceptions.InvalidRequest("Error occurred: inline labels must include Name!")

    previous_label = previous_labels.get(label.Name, None)
    if not previous_label:
        # put inline label that does not already exist
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
    else:
        # get existing label to get arn. Arn is readonly property, so it will not be attached to input model
        (
            get_labels_worked,
            get_labels_response,
        ) = validation_helpers.check_if_get_labels_succeeds(afd_client, label.Name)
        if not get_labels_worked:
            raise RuntimeError(f"Previously existing label {label.Name} no longer exists!")
        label.Arn = get_labels_response.get("labels")[0].get("arn")
        # put existing inline label and update tags
        common_helpers.put_inline_label(frauddetector_client=afd_client, label=label)
        if hasattr(label, "Tags"):
            common_helpers.update_tags(
                frauddetector_client=afd_client,
                afd_resource_arn=label.Arn,
                new_tags=label.Tags,
            )
