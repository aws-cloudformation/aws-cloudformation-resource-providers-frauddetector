from typing import Optional

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
