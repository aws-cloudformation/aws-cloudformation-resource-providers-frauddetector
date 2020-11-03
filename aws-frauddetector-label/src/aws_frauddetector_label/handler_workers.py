import logging
from cloudformation_cli_python_lib import (
    OperationStatus,
    exceptions,
)

from .helpers import common_helpers, client_helpers, validation_helpers, model_helpers, api_helpers
from .models import ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


def execute_create_label_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_create_duplicate, we need to fail if resource already exists
    get_labels_works, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, model.Name)
    if get_labels_works:
        raise exceptions.AlreadyExists('label', model.Name)

    # For contract_invalid_create, fail if any read-only properties are present
    if model.Arn is not None or model.CreatedTime is not None or model.LastUpdatedTime is not None:
        raise exceptions.InvalidRequest("Error occurred: cannot create read-only properties.")

    # API does not handle 'None' property gracefully
    if model.Tags is None:
        del model.Tags

    # after satisfying contract call put label
    return common_helpers.put_label_and_return_progress(afd_client, model, progress)


def execute_update_label_handler_work(session, model, progress, request):
    afd_client = client_helpers.get_singleton_afd_client(session)

    previous_resource_state: ResourceModel = request.previousResourceState

    # For contract_update_non_existent_resource, we need to fail if the resource DNE
    # get labels will throw RNF Exception if label DNE
    get_labels_works, get_labels_response = validation_helpers.check_if_get_labels_succeeds(afd_client, model.Name)
    if not get_labels_works:
        raise exceptions.NotFound('label', model.Name)

    # # For contract_update_create_only_property, we need to fail if trying to set Name to something different
    previous_name = previous_resource_state.Name
    if model.Name != previous_name:
        raise exceptions.NotUpdatable(f"Error occurred: cannot update create-only property 'Name'")

    labels_list = get_labels_response.get('labels', [])
    label = {}
    if len(labels_list) > 0:
        label = labels_list[0]
    label_arn = label.get('arn', '')
    if model.Tags is None:
        # API does not handle 'None' property gracefully
        del model.Tags
        common_helpers.update_tags(afd_client, afd_resource_arn=label_arn)
    else:
        # since put_label does not update tags, update tags separately
        # NOTE: currently, this won't remove tags when customers want to specifically remove tags...
        common_helpers.update_tags(afd_client, afd_resource_arn=label_arn, new_tags=model.Tags)

    # after satisfying contract call put label
    return common_helpers.put_label_and_return_progress(afd_client, model, progress)


def execute_delete_label_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_delete_delete, we need to fail if the resource DNE
    # get labels will throw RNF Exception if label DNE
    get_labels_works, _ = validation_helpers.check_if_get_labels_succeeds(afd_client, model.Name)
    if not get_labels_works:
        raise exceptions.NotFound('label', model.Name)

    try:
        api_helpers.call_delete_label(afd_client, model.Name)
        progress.resourceModel = None
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def execute_read_label_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    # For contract_delete_read, we need to fail if the resource DNE
    # get labels will throw RNF Exception if label DNE
    get_labels_works, get_labels_response = validation_helpers.check_if_get_labels_succeeds(afd_client, model.Name)
    if not get_labels_works:
        raise exceptions.NotFound('label', model.Name)

    try:
        labels = get_labels_response.get('labels', [])
        if len(labels) > 0:
            model = model_helpers.get_model_for_label(afd_client, labels[0])
        progress.resourceModel = model
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress


def execute_list_label_handler_work(session, model, progress):
    afd_client = client_helpers.get_singleton_afd_client(session)

    try:
        get_labels_response = api_helpers.call_get_labels(afd_client)
        labels = get_labels_response.get('labels', [])
        progress.resourceModels = [model_helpers.get_model_for_label(afd_client, label) for label in labels]
        progress.status = OperationStatus.SUCCESS
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred: {e}")
    return progress
