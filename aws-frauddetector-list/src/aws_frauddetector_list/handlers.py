import logging
from typing import Any, MutableMapping, Optional
from cloudformation_cli_python_lib import (
    Action,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
)

from . import handler_workers
from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

CALLBACK_STATUS_IN_PROGRESS = {
    "status": OperationStatus.IN_PROGRESS,
}
TYPE_NAME = "AWS::FraudDetector::List"

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
    if _is_callback(callback_context):
        return _callback_helper(
            session,
            request,
            callback_context,
            model,
        )
    LOG.info(f"calling create with the following request: {request}")
    return handler_workers.execute_create_list_handler_work(session, model, progress)


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
    return handler_workers.execute_update_list_handler_work(session, model, progress, request)


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    # Adding logs to temporarily fix unused var errors in pre-commit
    LOG.debug(model)
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=None,
    )
    LOG.info(f"calling delete with the following request: {request}")
    return handler_workers.execute_delete_list_handler_work(session, model, progress)


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
    return handler_workers.execute_read_list_handler_work(session, model, progress)


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
    return handler_workers.execute_list_list_handler_work(session, model, progress)


def _callback_helper(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
    model: Optional[ResourceModel],
) -> ProgressEvent:
    """Define a callback logic used for resource stabilization."""
    LOG.debug("_callback_helper()")

    # Call the Read handler to determine status.
    rh = read_handler(
        session,
        request,
        callback_context,
    )
    LOG.debug(f"Callback: Read handler status: {rh.status}")
    # Return success if the Read handler returns success.
    if rh.status == OperationStatus.SUCCESS:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=model,
        )
    elif rh.errorCode:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            resourceModel=model,
        )
    else:
        return ProgressEvent(
            status=OperationStatus.IN_PROGRESS,
            resourceModel=model,
        )


def _is_callback(
    callback_context: MutableMapping[str, Any],
) -> bool:
    """Logic to determine whether or not a handler invocation is new."""

    # If there is a callback context status set, then assume this is a
    # handler invocation (e.g., Create handler) for a previous request
    # that is still in progress.
    return callback_context.get("status") == CALLBACK_STATUS_IN_PROGRESS["status"]
