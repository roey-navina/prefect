from typing import TYPE_CHECKING

import prefect

if TYPE_CHECKING:
    from prefect.core.flow import Flow  # pylint: disable=W0611


def get_flow_image(flow: "Flow") -> str:
    """
    Retrieve the image to use for this flow deployment. Will start by looking for
    an `image` value in the flow's `environment.metadata`. If not found then it will fall
    back to using the `flow.storage`.

    Args:
        - flow (Flow): A flow object

    Returns:
        - str: a full image name to use for this flow run

    Raises:
        - ValueError: if deployment attempted on unsupported Storage type and `image` not
            present in environment metadata
    """
    environment = flow.environment
    if hasattr(environment, "metadata") and environment.metadata.get("image"):
        return environment.metadata.get("image", "")
    else:
        storage = flow.storage
        if not isinstance(storage, prefect.environments.storage.Docker,):
            raise ValueError(
                f"Storage for flow run {flow.name} is not of type Docker and environment has no `image` attribute in the metadata field."
            )

        return storage.name

def extract_flow_from_file(file_path: str = None, file_contents: str = None) -> "Flow":
    """
    Extract a flow object from a file
    """
    # TODO: Add support for passing name, otherwise get first flow found

    if file_path and file_contents:
        raise ValueError("Only one can be used")

    # Read file contents
    if file_path:
        with open(file_path, "r") as f:
            contents = f.read()

    # Use contents directly
    if file_contents:
        contents = file_contents

    # Load objects from file into dict
    exec_vals = {}
    exec(contents, exec_vals)

    # Grab flow name from values loaded via exec
    for var in exec_vals:
        if isinstance(exec_vals[var], prefect.Flow):
            # flow_name = exec_vals[var].name
            return exec_vals[var]

    raise ValueError(f"No flow found in {file_path}")