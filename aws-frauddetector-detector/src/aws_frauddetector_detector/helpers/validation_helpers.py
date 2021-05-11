import logging

from cloudformation_cli_python_lib import (
    exceptions,
)

from . import api_helpers, model_helpers
from .. import models

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def remove_none_arguments(args):
    keys_to_remove = {key for key, value in args.items() if value is None}
    for key in keys_to_remove:
        del args[key]
    return args


def check_if_get_detectors_succeeds(frauddetector_client, detector_id):
    """
    This calls get_detectors and returns True if it worked, along with the API response (True, response)
    If the call to get_detectors fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param detector_id:  the id of the detector you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_detectors_response = api_helpers.call_get_detectors(frauddetector_client, detector_id)
        return True, get_detectors_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting detector {detector_id}: {RNF}")
        return False, None


def check_if_get_detector_version_succeeds(frauddetector_client, detector_id, detector_version_id):
    """
    This calls get_detector_version and returns True if it worked, along with the API response (True, response)
    If the call to get_detector_version fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param detector_id:  the id of the detector you want to get
    :param detector_version_id:  the detector version id you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_detector_version_response = api_helpers.call_get_detector_version(
            frauddetector_client, detector_id, detector_version_id
        )
        return True, get_detector_version_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting detector {detector_id} version {detector_version_id}: {RNF}")
        return False, None


def check_if_get_variables_succeeds(frauddetector_client, variable_name):
    """
    This calls get_variables and returns True if it worked, along with the API response (True, response)
    If the call to get_variables fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param variable_name:  the name of the variable you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_variables_response = api_helpers.call_get_variables(frauddetector_client, variable_name)
        return True, get_variables_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting variable {variable_name}: {RNF}")
        return False, None


def check_if_get_entity_types_succeeds(frauddetector_client, entity_type_name):
    """
    This calls get_entity_types and returns True if it worked, along with the API response (True, response)
    If the call to get_entity_types fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param entity_type_name:  the name of the entity_type you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_entity_types_response = api_helpers.call_get_entity_types(frauddetector_client, entity_type_name)
        return True, get_entity_types_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting entity_type {entity_type_name}: {RNF}")
        return False, None


def check_if_get_event_types_succeeds(frauddetector_client, event_type_to_check: str):
    """
    This calls get_event_types and returns True if the response contains an event type: (True, event_type)
    If the call does not return any event types, return (False, None)
    :param frauddetector_client: frauddetector boto3 client
    :param event_type_to_check: the name of the event type to check for
    :return: a tuple: (bool, returned_event_type)
    """
    try:
        get_event_types_response = api_helpers.call_get_event_types(frauddetector_client, event_type_to_check)
        return True, get_event_types_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting event type {event_type_to_check}: {RNF}")
        return False, None


def check_if_get_labels_succeeds(frauddetector_client, label_name):
    """
    This calls get_labels and returns True if it worked, along with the API response (True, response)
    If the call to get_labels fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param label_name:  the name of the label you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_labels_response = api_helpers.call_get_labels(frauddetector_client, label_name)
        return True, get_labels_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting label {label_name}: {RNF}")
        return False, None


def check_if_get_outcomes_succeeds(frauddetector_client, outcome_name):
    """
    This calls get_outcomes and returns True if it worked, along with the API response (True, response)
    If the call to get_outcomes fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param outcome_name:  the name of the outcome you want to get
    :return: a tuple: (bool, apiResponse)
    """
    try:
        get_outcomes_response = api_helpers.call_get_outcomes(frauddetector_client, outcome_name)
        return True, get_outcomes_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting outcome {outcome_name}: {RNF}")
        return False, None


def check_if_get_model_version_succeeds(frauddetector_client, model_id, model_type, model_version_number):
    """
    This calls get_model_version and returns True if it worked, along with the API response (True, response)
    If the call to get_outcomes fails, this returns (False, None)
    :param frauddetector_client: afd boto3 client to use to make the request
    :param model_id:  the model id of the model you want to get
    :param model_type:  the model type of the model you want to get
    :param model_version_number: the model version number of the model version you want to get
    :return: a tuple: (bool, apiResponse)
    """

    try:
        get_model_version_response = api_helpers.call_get_model_version(
            frauddetector_client, model_id, model_type, model_version_number
        )
        return True, get_model_version_response
    except frauddetector_client.exceptions.ResourceNotFoundException as RNF:
        LOG.warning(f"Error getting model version {model_version_number} for model {model_id}: {RNF}")
        return False, None


def validate_external_models_for_detector_model(afd_client, model: models.ResourceModel):
    LOG.info("validating external models for detector")
    existing_external_model_response = api_helpers.call_get_external_models(afd_client)
    existing_external_models = existing_external_model_response.get("externalModels", [])
    existing_external_model_arns = {
        external_model.get("arn", "not/found") for external_model in existing_external_models
    }

    for requested_external_model_arn in model_helpers.get_external_model_arns_from_model(model):
        if requested_external_model_arn not in existing_external_model_arns:
            LOG.warning(f"validation failed for external model: {requested_external_model_arn}")
            raise exceptions.NotFound("associatedModel", requested_external_model_arn)


def check_variable_differences(existing_event_variable, desired_event_variable):
    return {
        "defaultValue": existing_event_variable.DefaultValue != desired_event_variable.DefaultValue,
        "description": existing_event_variable.Description != desired_event_variable.Description,
        "variableType": existing_event_variable.VariableType != desired_event_variable.VariableType,
        "dataType": existing_event_variable.DataType != desired_event_variable.DataType,
        "dataSource": existing_event_variable.DataSource != desired_event_variable.DataSource,
        "tags": existing_event_variable.Tags != desired_event_variable.Tags,
    }
