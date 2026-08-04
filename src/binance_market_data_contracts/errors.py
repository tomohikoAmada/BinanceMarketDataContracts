"""Contract error types."""


class ContractError(Exception):
    """Base class for contract-related errors."""


class ValidationError(ContractError):
    """A contract validation error."""


class SchemaVersionError(ContractError):
    """An unsupported or unknown schema version error."""

    def __init__(self, contract_name: str, requested_version: str, available_versions: list[str]) -> None:
        self.contract_name = contract_name
        self.requested_version = requested_version
        self.available_versions = available_versions
        super().__init__(
            f"Schema version '{requested_version}' for contract '{contract_name}' not found. "
            f"Available: {', '.join(available_versions)}"
        )
