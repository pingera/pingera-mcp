"""Organization secrets and the secrets injected into checks."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import CheckSecretsApi, SecretsApi
from pingera.models import CheckSecret, Secret1, Secret2
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import CheckId, PageNumber, PageSize

SecretId = Annotated[str, Field(description="Secret ID (see list_secrets).")]
_EXCLUDE = {"created_by", "updated_by"}


@tool("secrets")
def list_secrets(page: PageNumber = None, page_size: PageSize = None) -> Any:
    """List the organization's secrets (names and IDs; values are not returned)."""
    return api(SecretsApi).v1_secrets_get(page=page, page_size=page_size)


@tool("secrets")
def get_secret(secret_id: SecretId) -> Any:
    """Get a secret. The value is only included for users allowed to edit secrets."""
    return api(SecretsApi).v1_secrets_secret_id_get(secret_id=secret_id)


model_tool(
    "secrets",
    "create_secret",
    model=Secret1,
    exclude=_EXCLUDE,
    required={"secret_value"},
    call=lambda body: api(SecretsApi).v1_secrets_post(secret1=body),
    description=(
        "Store a secret (API token, password...) encrypted. Checks get it as an environment variable once attached "
        "with add_check_secret or the `secrets` field of create/update_check."
    ),
)

model_tool(
    "secrets",
    "update_secret",
    model=Secret2,
    partial=True,
    exclude=_EXCLUDE,
    path=[("secret_id", "ID of the secret.")],
    call=lambda body, secret_id: api(SecretsApi).v1_secrets_secret_id_patch(secret_id=secret_id, secret2=body),
    idempotent=True,
    description="Rename a secret or change its value. Checks using it get the new value on their next run.",
)


@tool("secrets", access="write", destructive=True, idempotent=True)
def delete_secret(secret_id: SecretId) -> Any:
    """Delete a secret. Checks that use it lose the environment variable."""
    return api(SecretsApi).v1_secrets_secret_id_delete(secret_id=secret_id)


@tool("secrets")
def list_check_secrets(check_id: CheckId) -> Any:
    """List the secrets attached to a check and their environment variable names."""
    return api(CheckSecretsApi).v1_checks_check_id_secrets_get(check_id=check_id)


@tool("secrets", access="write", idempotent=True)
def add_check_secret(
    check_id: CheckId,
    secret_id: SecretId,
    env_variable: Annotated[str, Field(max_length=100, description="Environment variable name, e.g. API_TOKEN.")],
) -> Any:
    """Attach a secret to a check; scripts read it as process.env.<env_variable>."""
    return api(CheckSecretsApi).v1_checks_check_id_secrets_post(
        check_id=check_id, check_secret=CheckSecret(secret_id=secret_id, env_variable=env_variable)
    )


@tool("secrets", access="write", idempotent=True)
def remove_check_secret(check_id: CheckId, secret_id: SecretId) -> Any:
    """Detach a secret from a check (the secret itself is kept)."""
    return api(CheckSecretsApi).v1_checks_check_id_secrets_secret_id_delete(check_id=check_id, secret_id=secret_id)
