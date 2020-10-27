from cloudformation_cli_python_lib import (
    SessionProxy,
    exceptions,
)


# Use this global and use `afd_client = get_singleton_afd_client(session)` for singleton
afd_client = None


def get_singleton_afd_client(session):
    global afd_client
    if afd_client is not None:
        return afd_client
    if isinstance(session, SessionProxy):
        afd_client = session.client("frauddetector")
        return afd_client
    raise exceptions.InternalFailure(f"Error: failed to get frauddetector client.")
