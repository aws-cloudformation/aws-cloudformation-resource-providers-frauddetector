from botocore.config import Config
from cloudformation_cli_python_lib import (
    SessionProxy,
    exceptions,
)


BOTO3_CLIENT_CONFIG_WITH_STANDARD_RETRIES = Config(retries={"total_max_attempts": 3, "mode": "standard"})


def get_afd_client(session):
    if isinstance(session, SessionProxy):
        return session.client(
            service_name="frauddetector",
            config=BOTO3_CLIENT_CONFIG_WITH_STANDARD_RETRIES,
        )
    raise exceptions.InternalFailure(f"Error: failed to get frauddetector client.")
