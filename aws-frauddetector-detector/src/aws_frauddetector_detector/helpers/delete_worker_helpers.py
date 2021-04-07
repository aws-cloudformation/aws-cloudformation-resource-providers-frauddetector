import logging

from . import api_helpers, model_helpers
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


ACTIVE_STATUS = 'ACTIVE'
INACTIVE_STATUS = 'INACTIVE'


def deactivate_and_delete_detector_versions_for_detector_model(afd_client, detector_model: models.ResourceModel):
    describe_detector_response = api_helpers.call_describe_detector(frauddetector_client=afd_client,
                                                                    detector_id=detector_model.DetectorId)
    dv_summaries = describe_detector_response.get('detectorVersionSummaries', [])
    for dv in dv_summaries:
        if dv.get('status', '') == ACTIVE_STATUS:
            api_helpers.call_update_detector_version_status(
                frauddetector_client=afd_client,
                detector_id=detector_model.DetectorId,
                detector_version_id=dv.get('detectorVersionId', '-1'),
                status=INACTIVE_STATUS
            )
        api_helpers.call_delete_detector_version(
            frauddetector_client=afd_client,
            detector_id=detector_model.DetectorId,
            detector_version_id=dv.get('detectorVersionId', '-1')
        )


def delete_rules_and_inline_outcomes_for_detector_model(afd_client, detector_model: models.ResourceModel):
    # get rules: id -> rules
    get_rules_response = api_helpers.call_get_rules(
        frauddetector_client=afd_client,
        detector_id=detector_model.DetectorId
    )
    rule_details = get_rules_response.get('ruleDetails', [])
    rule_models_by_rule_id_version = _create_rule_models_by_rule_id_rule_version_tuple(detector_model)
    inline_outcome_names = set()
    for rule_detail in rule_details:
        rule_id = rule_detail.get('ruleId', '')
        rule_version = rule_detail.get('ruleVersion', '-1')

        # Check if rule is defined in CFN, and collect inline outcomes if so
        rule_id_version_tuple = (rule_id, rule_version)
        if rule_id_version_tuple in rule_models_by_rule_id_version:
            rule_model = rule_models_by_rule_id_version[rule_id_version_tuple]
            inline_outcome_names.update([outcome.Name for outcome in rule_model.Outcomes if outcome.Inline])

        # delete rule
        api_helpers.call_delete_rule(
            frauddetector_client=afd_client,
            detector_id=detector_model.DetectorId,
            rule_id=rule_id,
            rule_version=rule_version
        )

    for outcome_name in inline_outcome_names:
        api_helpers.call_delete_outcome(
            frauddetector_client=afd_client,
            outcome_name=outcome_name
        )
    return


def delete_detector_for_detector_model(afd_client, detector_model: models.ResourceModel):
    api_helpers.call_delete_detector(
        frauddetector_client=afd_client,
        detector_id=detector_model.DetectorId
    )


def delete_inline_dependencies_for_detector_model(afd_client, detector_model: models.ResourceModel):
    if detector_model.EventType.Inline:
        _delete_inline_dependencies_for_inline_event_type(afd_client, detector_model.EventType)
        # delete event type
        api_helpers.call_delete_event_type(
            frauddetector_client=afd_client,
            event_type_name=detector_model.EventType.Name
        )


def _create_rule_models_by_rule_id_rule_version_tuple(detector_model: models.ResourceModel):
    dict_to_return = {}
    if not detector_model.Rules:
        return dict_to_return
    for rule in detector_model.Rules:
        dict_to_return[(rule.RuleId, rule.RuleVersion)] = rule
    return dict_to_return


def _delete_inline_dependencies_for_inline_event_type(afd_client, event_type_model: models.EventType):
    inline_resources = model_helpers.get_inline_resources_for_event_type(event_type_model=event_type_model)
    _delete_inline_event_variables(afd_client, inline_resources['event_variables'])
    _delete_inline_entity_types(afd_client, inline_resources['entity_types'])
    _delete_inline_labels(afd_client, inline_resources['labels'])


def _delete_inline_event_variables(afd_client, inline_variable_names: set):
    for inline_variable_name in inline_variable_names:
        api_helpers.call_delete_variable(frauddetector_client=afd_client, variable_name=inline_variable_name)


def _delete_inline_entity_types(afd_client, inline_entity_type_names: set):
    for inline_entity_type_name in inline_entity_type_names:
        api_helpers.call_delete_entity_type(frauddetector_client=afd_client, entity_type_name=inline_entity_type_name)


def _delete_inline_labels(afd_client, inline_label_names: set):
    for inline_label_name in inline_label_names:
        api_helpers.call_delete_label(frauddetector_client=afd_client, label_name=inline_label_name)
