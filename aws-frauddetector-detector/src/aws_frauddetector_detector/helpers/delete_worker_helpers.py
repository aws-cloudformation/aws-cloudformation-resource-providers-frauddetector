import logging

from . import api_helpers, model_helpers
from ..models import ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


def delete_inline_dependencies(afd_client, model: ResourceModel):
    inline_resources = model_helpers.get_inline_resources(event_type_model=model)

    _delete_inline_event_variables(afd_client, inline_resources['event_variables'])
    _delete_inline_entity_types(afd_client, inline_resources['entity_types'])
    _delete_inline_labels(afd_client, inline_resources['labels'])


def _delete_inline_event_variables(afd_client, inline_variable_names: set):
    for inline_variable_name in inline_variable_names:
        api_helpers.call_delete_variable(frauddetector_client=afd_client, variable_name=inline_variable_name)


def _delete_inline_entity_types(afd_client, inline_entity_type_names: set):
    for inline_entity_type_name in inline_entity_type_names:
        api_helpers.call_delete_entity_type(frauddetector_client=afd_client, entity_type_name=inline_entity_type_name)


def _delete_inline_labels(afd_client, inline_label_names: set):
    for inline_label_name in inline_label_names:
        api_helpers.call_delete_label(frauddetector_client=afd_client, label_name=inline_label_name)
