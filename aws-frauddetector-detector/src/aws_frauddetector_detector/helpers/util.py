from typing import Optional


# This works because afd does not support '/' in any identifiers, e.g. external model endpoint name
EXTERNAL_MODEL_ARN_SUBSTRING = "external-model/"


def extract_name_from_arn(resource_arn: str) -> Optional[str]:
    if resource_arn is None:
        return None
    return resource_arn.split("/")[-1]


def is_arn_external_model_arn(arn: str) -> bool:
    return EXTERNAL_MODEL_ARN_SUBSTRING in arn
