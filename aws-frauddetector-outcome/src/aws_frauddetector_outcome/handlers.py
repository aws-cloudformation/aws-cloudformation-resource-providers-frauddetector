import logging
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from . import handler_workers
from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

TYPE_NAME = "AWS::FraudDetector::Outcome"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info(f"calling create with the following request: {request}")
    return handler_workers.execute_create_outcome_handler_work(session, model, progress)


@resource.handler(Action.UPDATE)
def update_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info(f"calling update with the following request: {request}")
    return handler_workers.execute_update_outcome_handler_work(session, model, progress, request)


@resource.handler(Action.DELETE)
def delete_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info(f"calling delete with the following request: {request}")
    return handler_workers.execute_delete_outcome_handler_work(session, model, progress)


@resource.handler(Action.READ)
def read_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info(f"calling read with the following request: {request}")
    return handler_workers.execute_read_outcome_handler_work(session, model, progress)


@resource.handler(Action.LIST)
def list_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info(f"calling list with the following request: {request}")
    return handler_workers.execute_list_outcome_handler_work(session, model, progress)
