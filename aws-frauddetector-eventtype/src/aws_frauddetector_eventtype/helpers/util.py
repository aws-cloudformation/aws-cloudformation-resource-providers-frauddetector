from typing import Optional


def extract_name_from_arn(resource_arn: str) -> Optional[str]:
    if resource_arn is None:
        return None
    return resource_arn.split("/")[-1]


def split_array_into_chunks(arr, chunk_size):
    """
    Return a generator of arrays of length chunk_size from source array arr.
    """
    for i in range(0, len(arr), chunk_size):
        yield arr[i : i + chunk_size]
    return
