import logging
from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
)

from .helpers import common_helpers, client_helpers, validation_helpers, model_helpers, api_helpers
from .models import ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


def execute_create_entity_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_create_duplicate, we need to fail if resource already exists
    get_entity_types_works, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, model.Name)
    if get_entity_types_works:
        raise exceptions.AlreadyExists('entity_type', model.Name)

    # For contract_invalid_create, fail if any read-only properties are present
    if model.Arn is not None or model.CreatedTime is not None or model.LastUpdatedTime is not None:
        raise exceptions.InvalidRequest("Error occurred: cannot create read-only properties.")

    # API does not handle 'None' property gracefully
    if model.Tags is None:
        del model.Tags

    # after satisfying contract call put entity_type
    return common_helpers.put_entity_type_and_return_progress(afd_client, model, progress)


def execute_update_entity_type_handler_work(session, model, progress, request):
    afd_client = client_helpers.get_singleton_afd_client(session)

    previous_resource_state: ResourceModel = request.previousResourceState

    # For contract_update_non_existent_resource, we need to fail if the resource DNE
    # get entity_types will throw RNF Exception if entity_type DNE
    get_entity_types_works, get_entity_types_response =\
        validation_helpers.check_if_get_entity_types_succeeds(afd_client, model.Name)
    if not get_entity_types_works:
        raise exceptions.NotFound('entity_type', model.Name)

    # # For contract_update_create_only_property, we need to fail if trying to set Name to something different
    previous_name = previous_resource_state.Name
    if model.Name != previous_name:
        raise exceptions.NotUpdatable(f"Error occurred: cannot update create-only property 'Name'")

    if model.Tags is None:
        # API does not handle 'None' property gracefully
        del model.Tags
        common_helpers.update_tags(afd_client, afd_resource_arn=model.Arn)
    else:
        # since put_entity_type does not update tags, update tags separately
        common_helpers.update_tags(afd_client, afd_resource_arn=model.Arn, new_tags=model.Tags)

    # after satisfying contract call put entity_type
    return common_helpers.put_entity_type_and_return_progress(afd_client, model, progress)


def execute_delete_entity_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_delete_delete, we need to fail if the resource DNE
    # get entity_types will throw RNF Exception if entity_type DNE
    get_entity_types_works, _ = validation_helpers.check_if_get_entity_types_succeeds(afd_client, model.Name)
    if not get_entity_types_works:
        raise exceptions.NotFound('entity_type', model.Name)

    try:
        api_helpers.call_delete_entity_type(afd_client, model.Name)
        progress.resourceModel = None
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def execute_read_entity_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)
    # read requests only include primary identifier (Arn). Extract Name from Arn
    model.Name = model.Arn.split('/')[-1]

    # For contract_delete_read, we need to fail if the resource DNE
    # get entity_types will throw RNF Exception if entity_type DNE
    get_entity_types_works, get_entity_types_response = validation_helpers.check_if_get_entity_types_succeeds(afd_client, model.Name)
    if not get_entity_types_works:
        raise exceptions.NotFound('entity_type', model.Name)

    try:
        entity_types = get_entity_types_response.get('entityTypes', [])
        if entity_types:
            model = model_helpers.get_model_for_entity_type(afd_client, entity_types[0])
        progress.resourceModel = model
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def execute_list_entity_type_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    try:
        get_entity_types_response = api_helpers.call_get_entity_types(afd_client)
        entity_types = get_entity_types_response.get('entityTypes', [])
        progress.resourceModels = [model_helpers.get_model_for_entity_type(afd_client, entity_type) for entity_type in entity_types]
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress
