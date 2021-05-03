import logging
from cloudformation_cli_python_lib import (
    exceptions,
)

from . import validation_helpers, model_helpers
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def validate_detector_exists_and_return_detector_resource_model(
    afd_client, model: models.ResourceModel
) -> models.ResourceModel:
    # For contract_delete_read, we need to fail if the resource DNE
    (
        get_detectors_works,
        get_detectors_response,
    ) = validation_helpers.check_if_get_detectors_succeeds(afd_client, model.DetectorId)

    if not get_detectors_works:
        raise exceptions.NotFound("detector", model.DetectorId)

    try:
        detectors = get_detectors_response.get("detectors", [])
        if not detectors:
            raise exceptions.NotFound("detector", model.DetectorId)
        return model_helpers.get_model_for_detector(afd_client, detectors[0], model)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
