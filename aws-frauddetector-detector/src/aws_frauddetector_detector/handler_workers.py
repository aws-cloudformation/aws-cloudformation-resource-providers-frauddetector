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
    update_worker_helpers,
    delete_worker_helpers,
    api_helpers
)

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def execute_create_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    pass


def execute_update_detector_handler_work(session: SessionProxy,
                                         model: models.ResourceModel,
                                         progress: ProgressEvent,
                                         request):
    pass


def execute_delete_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    pass


def execute_read_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    afd_client = client_helpers.get_singleton_afd_client(session)
    # read requests only include primary identifier (Arn). Extract DetectorId from Arn
    if not model.DetectorId:
        model.DetectorId = model.Arn.split('/')[-1]

    # For contract_delete_read, we need to fail if the resource DNE
    get_detectors_works, get_detectors_response = validation_helpers.check_if_get_detectors_succeeds(afd_client,
                                                                                                     model.DetectorId)

    if not get_detectors_works:
        raise exceptions.NotFound('detector', model.DetectorId)

    try:
        detectors = get_detectors_response.get('detectors', [])
        if not detectors:
            raise exceptions.NotFound('detector', model.DetectorId)
        model = model_helpers.get_model_for_detector(afd_client, detectors[0], model)
        progress.resourceModel = model
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")


def execute_list_detector_handler_work(session: SessionProxy, model: models.ResourceModel, progress: ProgressEvent):
    pass
