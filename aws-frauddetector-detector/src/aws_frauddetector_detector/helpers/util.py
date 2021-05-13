from typing import Optional
from cloudformation_cli_python_lib import (
    exceptions,
)

# This works because afd does not support '/' in any identifiers, e.g. external model endpoint name
EXTERNAL_MODEL_ARN_SUBSTRING = "external-model/"

MODEL_VERSION_ARN_SUBSTRING = "model-version/"
MODEL_VERSION_ARN_SEGMENTS = 4


def extract_name_from_arn(resource_arn: str) -> Optional[str]:
    if resource_arn is None:
        return None
    return resource_arn.split("/")[-1]


def is_external_model_arn(arn: str) -> bool:
    return EXTERNAL_MODEL_ARN_SUBSTRING in arn


def is_model_version_arn(arn: str) -> bool:
    return MODEL_VERSION_ARN_SUBSTRING in arn and len(arn.split("/")) == MODEL_VERSION_ARN_SEGMENTS


def get_model_version_details_from_arn(arn):
    if not is_model_version_arn(arn):
        raise exceptions.InvalidRequest("Unexpected ARN provided in AssociatedModels: {}".format(arn))

    segmented_arn = arn.split("/")
    model_version_number = segmented_arn[-1]
    model_id = segmented_arn[-2]
    model_type = segmented_arn[-3]
    return model_id, model_type, model_version_number
