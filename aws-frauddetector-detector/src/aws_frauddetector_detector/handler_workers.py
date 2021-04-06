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
    api_helpers
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

    # API does not handle 'None' property gracefully
    if model.Tags is None:
        del model.Tags

    # Validate existence of referenced resources, validate and create inline resources (except for Rules, Detector)
    # TODO: split out creation from validation
    create_worker_helpers.validate_dependencies_for_detector_create(afd_client, model)

    # Create Detector, Rules, Detector Version ID
    model_helpers.put_detector_for_model(afd_client, model)
    rule_dicts = create_worker_helpers.create_rules_for_detector_resource(afd_client, model)
    detector_version_response = create_worker_helpers.create_detector_version_for_detector_resource(afd_client,
                                                                                                    model,
                                                                                                    rule_dicts)
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
    pass


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
