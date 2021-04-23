from cloudformation_cli_python_lib import (
    SessionProxy,
    exceptions,
)


def get_afd_client(session):
    if isinstance(session, SessionProxy):
        return session.client("frauddetector")

    raise exceptions.InternalFailure(f"Error: failed to get frauddetector client.")
