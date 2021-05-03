from typing import Optional


def extract_name_from_arn(resource_arn: str) -> Optional[str]:
    if resource_arn is None:
        return None
    return resource_arn.split("/")[-1]
