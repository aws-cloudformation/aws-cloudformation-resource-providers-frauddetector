import logging
from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
)

from .models import ResourceModel
from .helpers import (
    common_helpers,
    client_helpers,
    validation_helpers,
    model_helpers,
    create_worker_helpers,
    update_worker_helpers,
    delete_worker_helpers,
    api_helpers,
)

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def execute_create_event_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_afd_client(session)

    # For contract_create_duplicate, we need to fail if the resource already exists
    get_event_type_works, _ = validation_helpers.check_if_get_event_types_succeeds(afd_client, model.Name)
    if get_event_type_works:
        raise exceptions.AlreadyExists("event_type", model.Name)

    # For contract_invalid_create, fail if any read-only properties are present
    if model.Arn is not None or model.CreatedTime is not None or model.LastUpdatedTime is not None:
        raise exceptions.InvalidRequest("Error occurred: cannot create read-only properties.")

    # Validate existence of referenced resources, validate and create inline resources
    create_worker_helpers.validate_dependencies_for_create(afd_client, model)

    # after satisfying contract call put event_type
    return common_helpers.put_event_type_and_return_progress(afd_client, model, progress)


def execute_update_event_type_handler_work(session, model, progress, request):
    afd_client = client_helpers.get_afd_client(session)

    previous_resource_state: ResourceModel = request.previousResourceState

    # For contract_update_non_existent_resource, we need to fail if the resource DNE
    # get_event_types will throw RNF Exception if event_type DNE
    get_event_type_works, _ = validation_helpers.check_if_get_event_types_succeeds(afd_client, model.Name)
    if not get_event_type_works:
        raise exceptions.NotFound("event_type", model.Name)

    # # For contract_update_create_only_property, we need to fail if trying to set Name to something different
    previous_name = previous_resource_state.Name
    if model.Name != previous_name:
        raise exceptions.NotUpdatable(f"Error occurred: cannot update create-only property 'Name'")

    # Validate existence of referenced resources, validate and update inline resources
    LOG.debug(f"validating dependencies for update ...")
    update_worker_helpers.validate_dependencies_for_update(afd_client, model, previous_resource_state)

    # since put_event_type does not update tags, update tags separately
    LOG.debug(f"updating tags for model ...")
    common_helpers.update_tags(afd_client, afd_resource_arn=model.Arn, new_tags=model.Tags)

    # after satisfying contract call put event_type
    return common_helpers.put_event_type_and_return_progress(afd_client, model, progress)


def execute_delete_event_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_afd_client(session)

    # For contract_delete_delete, we need to fail if the resource DNE
    # get_event_types will throw RNF Exception if event_type DNE
    get_event_type_works, get_response = validation_helpers.check_if_get_event_types_succeeds(afd_client, model.Name)
    if not get_event_type_works:
        raise exceptions.NotFound("event_type", model.Name)

    # Check for existing events
    loaded_event_types = get_response.get("eventTypes", [])
    if loaded_event_types:
        ingested_event_stats = loaded_event_types[0].get("ingestionStatistics", {})
        ingested_count = ingested_event_stats.get("numberOfEvents", 0)
        if ingested_count > 0:
            raise exceptions.InvalidRequest(
                f"Error occurred: cannot delete event type '{model.Name}' because it has {ingested_count} "
                + "events ingested. Use the DeleteEventsByEventType API or the DeleteEvent API to remove "
                + "ingested events and try again."
            )

    try:
        LOG.debug("deleting event type")
        api_helpers.call_delete_event_type(afd_client, model.Name)
        LOG.debug("deleting inline dependencies (entity types, labels, event variables)")
        delete_worker_helpers.delete_inline_dependencies(afd_client, model)
        progress.resourceModel = None
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_read_event_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_afd_client(session)
    # read requests only include primary identifier (Arn). Extract Name from Arn
    if not model.Name:
        model.Name = model.Arn.split("/")[-1]

    # For contract_delete_read, we need to fail if the resource DNE
    # get_event_types will throw RNF Exception if event_type DNE
    (
        get_event_types_works,
        get_event_types_response,
    ) = validation_helpers.check_if_get_event_types_succeeds(afd_client, model.Name)
    if not get_event_types_works:
        raise exceptions.NotFound("event_type", model.Name)

    try:
        event_types = get_event_types_response.get("eventTypes", [])
        if event_types:
            referenced_resources = model_helpers.get_referenced_resources(model)
            model = model_helpers.get_model_for_event_type(afd_client, event_types[0], referenced_resources)
        else:
            raise exceptions.NotFound("event_type", model.Name)
        progress.resourceModel = model
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress


def execute_list_event_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_afd_client(session)

    try:
        get_event_types_response = api_helpers.call_get_event_types(afd_client)
        event_types = get_event_types_response.get("eventTypes", [])

        # Assume inline for list handler (we have no way of knowing with current implementation)
        empty_references = model_helpers.get_referenced_resources(None)
        progress.resourceModels = [
            model_helpers.get_model_for_event_type(afd_client, et, empty_references) for et in event_types
        ]
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    LOG.info(f"Returning Progress with status: {progress.status}")
    return progress
