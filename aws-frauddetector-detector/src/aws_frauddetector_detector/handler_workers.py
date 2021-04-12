import logging
from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
    ProgressEvent,
    SessionProxy
)

from . import models
from .helpers import (
    common_helpers,
    client_helpers,
    validation_helpers,
    model_helpers,
    create_worker_helpers,
    read_worker_helpers,
    list_worker_helpers,
    update_worker_helpers,
    delete_worker_helpers,
    api_helpers,
    util
)

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


DRAFT_STATUS = 'DRAFT'


def execute_create_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_create_duplicate, we need to fail if the resource already exists
    get_detectors_works, _ = validation_helpers.check_if_get_detectors_succeeds(afd_client, model.DetectorId)
    if get_detectors_works:
        raise exceptions.AlreadyExists('detector', model.DetectorId)

    # For contract_invalid_create, fail if any read-only properties are present
    if model.Arn is not None or model.CreatedTime is not None or model.LastUpdatedTime is not None:
        raise exceptions.InvalidRequest("Error occurred: cannot create read-only properties.")

    # Validate existence of referenced resources, validate and create inline resources (except for Rules, Detector, DV)
    # TODO: split out creation from validation
    create_worker_helpers.validate_dependencies_for_detector_create(afd_client, model)

    # Create Detector, Rules, Detector Version ID
    model_helpers.put_detector_for_model(afd_client, model)
    rule_dicts = create_worker_helpers.create_rules_for_detector_resource(afd_client, model)
    detector_version_response = create_worker_helpers.create_detector_version_for_detector_resource(afd_client,
                                                                                                    model,
                                                                                                    rule_dicts)

    # The DV will be created as draft by default, so if the desired status is not draft, update DV status
    if model.DetectorVersionStatus != DRAFT_STATUS:
        api_helpers.call_update_detector_version_status(
            frauddetector_client=afd_client,
            detector_id=model.DetectorId,
            detector_version_id=detector_version_response.get('detectorVersionId', '1'),  # version here should be 1
            status=model.DetectorVersionStatus
        )

    # after satisfying all contract tests and AFD requirements, get the resulting model
    model = read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(afd_client, model)
    progress.resourceModel = model
    progress.status = OperationStatus.SUCCESS

    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_update_detector_handler_work(session: SessionProxy,
                                         model: models.ResourceModel,
                                         progress: ProgressEvent,
                                         request):
    afd_client = client_helpers.get_singleton_afd_client(session)

    previous_resource_state: models.ResourceModel = request.previousResourceState

    # For contract_update_create_only_property, we need to fail if trying to set DetectorId to something different
    if model.DetectorId != previous_resource_state.DetectorId:
        raise exceptions.NotUpdatable(f"Error occurred: cannot update create-only property 'DetectorId'")

    # For contract_update_non_existent_resource, we need to fail if the resource DNE
    get_detectors_works, _ = validation_helpers.check_if_get_detectors_succeeds(afd_client, model.DetectorId)
    if not get_detectors_works:
        raise exceptions.NotFound('detector', model.DetectorId)

    # Validate existence of dependencies for update (just eventtype for now)
    LOG.debug(f"validating dependencies for update ...")
    update_worker_helpers.validate_dependencies_for_detector_update(afd_client, model, previous_resource_state)

    # Update inline event type and inline event type dependencies
    if model.EventType.Inline:
        update_worker_helpers.validate_dependencies_for_inline_event_type_update(
            afd_client=afd_client,
            event_type_model=model.EventType,
            previous_event_type_model=previous_resource_state.EventType
        )

    # Create/Update rules and inline outcomes
    rule_versions_to_delete, outcomes_to_delete =\
        update_worker_helpers.update_rules_and_inline_outcomes_for_detector_update(
            afd_client=afd_client,
            model=model,
            previous_model=previous_resource_state
        )

    # Create/Update DV, set active if desired status is active
    detector_versions_to_delete = update_worker_helpers.update_detector_version_for_detector_update(
        afd_client=afd_client,
        model=model,
        previous_model=previous_resource_state
    )

    # Delete old DVs
    update_worker_helpers.delete_unused_detector_versions_for_detector_update(
        afd_client=afd_client,
        unused_detector_versions=detector_versions_to_delete
    )

    # Delete old rules that are no longer used
    update_worker_helpers.delete_unused_rules_for_detector_update(
        afd_client=afd_client,
        detector_id=model.DetectorId,
        unused_rule_versions=rule_versions_to_delete
    )

    # Delete old inline outcomes that are no longer present in the rules
    update_worker_helpers.delete_unused_inline_outcomes_for_detector_update(
        afd_client=afd_client,
        unused_inline_outcome_names=outcomes_to_delete
    )

    # Put detector (for description update)
    if model.EventType.Name:
        event_type_name = model.EventType.Name
    else:
        event_type_name = util.extract_name_from_arn(model.EventType.Arn)
    api_helpers.call_put_detector(
        frauddetector_client=afd_client,
        detector_id=model.DetectorId,
        detector_event_type_name=event_type_name,
        detector_description=model.Description
    )

    LOG.debug(f"updating tags for model ...")
    # since put on update does not update tags, update tags separately
    common_helpers.update_tags(afd_client, afd_resource_arn=model.Arn, new_tags=model.Tags)

    # after satisfying all contract tests and AFD requirements, get the resulting model
    model = read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(afd_client, model)
    progress.resourceModel = model
    progress.status = OperationStatus.SUCCESS

    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_delete_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_delete_delete, we need to fail if the resource DNE
    get_detectors_works, _ = validation_helpers.check_if_get_detectors_succeeds(afd_client, model.DetectorId)
    if not get_detectors_works:
        raise exceptions.NotFound('detector', model.DetectorId)

    try:
        LOG.debug("deleting DVs")
        delete_worker_helpers.deactivate_and_delete_detector_versions_for_detector_model(afd_client, model)

        LOG.debug("deleting Rules (+ outcomes)")
        delete_worker_helpers.delete_rules_and_inline_outcomes_for_detector_model(afd_client, model)

        LOG.debug("deleting detector")
        delete_worker_helpers.delete_detector_for_detector_model(afd_client, model)

        LOG.debug("deleting inline dependencies (event type: entity types, labels, event variables)")
        delete_worker_helpers.delete_inline_dependencies_for_detector_model(afd_client, model)

        progress.resourceModel = None
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_read_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    afd_client = client_helpers.get_singleton_afd_client(session)
    # read requests only include primary identifier (Arn). Extract DetectorId from Arn
    if not model.DetectorId:
        model.DetectorId = model.Arn.split('/')[-1]

    model = read_worker_helpers.validate_detector_exists_and_return_detector_resource_model(afd_client, model)
    progress.resourceModel = model
    progress.status = OperationStatus.SUCCESS

    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_list_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    afd_client = client_helpers.get_singleton_afd_client(session)
    try:
        detector_models = list_worker_helpers.list_detector_models(afd_client)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    progress.resourceModels = detector_models
    progress.status = OperationStatus.SUCCESS
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress
