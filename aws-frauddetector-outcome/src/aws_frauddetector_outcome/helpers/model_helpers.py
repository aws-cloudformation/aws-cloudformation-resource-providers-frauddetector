from typing import List
from cloudformation_cli_python_lib import exceptions
from ..models import ResourceModel, Tag
from . import api_helpers

import logging

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)


def get_tags_from_tag_models(tag_models: List[Tag]):
    # boto3 afd client doesn't know about the 'Tags' class that cfn creates
    return [{"key": tag.Key, "value": tag.Value} for tag in tag_models]


def get_tag_models_from_tags(tags: List[dict]):
    # we need to translate our afd tags back to a list of cfn Tag
    return [Tag(Key=tag.get('key', ''), Value=tag.get('value', '')) for tag in tags]


def get_model_for_outcome(frauddetector_client, outcome):
    outcome_arn = outcome.get('arn', '')
    list_tags_response = api_helpers.call_list_tags_for_resource(frauddetector_client, resource_arn=outcome_arn)
    attached_tags = list_tags_response.get("tags", [])
    tag_models = get_tag_models_from_tags(attached_tags)
    return ResourceModel(
        Name=outcome.get('name', ''),
        Arn=outcome_arn,
        Tags=tag_models,
        Description=outcome.get('description', ''),
        CreatedTime=outcome.get('createdTime', ''),
        LastUpdatedTime=outcome.get('lastUpdatedTime', '')
    )


def get_outcomes_and_return_model_for_outcome(frauddetector_client, outcome_name):
    try:
        get_outcomes_response = api_helpers.call_get_outcomes(frauddetector_client, outcome_name=outcome_name)
        outcomes = get_outcomes_response.get('outcomes', [])
        if len(outcomes) > 0:
            return get_model_for_outcome(frauddetector_client, outcomes[0])
        # if get outcomes worked but did not return any outcomes, we have major problems
        error_msg = f"get_outcomes for {outcome_name} worked but did not return any outcomes!"
        LOG.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        raise exceptions.InternalFailure(f"Error occurred while getting an outcome: {e}")
