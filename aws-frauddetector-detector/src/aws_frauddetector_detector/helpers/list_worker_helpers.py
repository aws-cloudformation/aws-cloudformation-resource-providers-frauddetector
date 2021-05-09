import logging
from typing import List

from . import api_helpers, model_helpers
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def list_detector_models(afd_client) -> List[models.ResourceModel]:
    # For contract_delete_read, we need to fail if the resource DNE
    get_detectors_response = api_helpers.call_get_detectors(afd_client)
    detectors_in_response = get_detectors_response.get("detectors", [])

    models_to_return = []
    for detector in detectors_in_response:
        # get_model_for_detector requires model.EventType.Name and model.EventType.Inline
        # Assume Inline for list handler (we have no way of knowing with current implementation)
        empty_event_type_model = models.EventType(
            Name=detector.get("eventTypeName", None),
            Tags=[],
            Description=None,
            EventVariables=[],
            Labels=[],
            EntityTypes=[],
            Arn=None,
            CreatedTime=None,
            LastUpdatedTime=None,
            Inline=True,
        )
        partial_model = models.ResourceModel(
            DetectorId=detector.get("detectorId", ""),
            Arn=detector.get("arn", ""),
            CreatedTime=detector.get("createdTime", ""),
            LastUpdatedTime=detector.get("lastUpdatedTime", ""),
            Description=detector.get("description", None),
            EventType=empty_event_type_model,
            DetectorVersionId=None,
            DetectorVersionStatus=None,
            RuleExecutionMode=None,
            Rules=[],
            Tags=None,
            AssociatedModels=None,
        )
        populated_model = model_helpers.get_model_for_detector(afd_client, detector, partial_model)
        models_to_return.append(populated_model)
    return models_to_return
