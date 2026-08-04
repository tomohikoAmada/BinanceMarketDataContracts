"""Test golden fixtures: Pydantic + JSON Schema validation with strict manifest."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from binance_market_data_contracts.schema_export import export_schemas
from binance_market_data_contracts.versions import CONTRACT_REGISTRY

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"


class ValidationScope(StrEnum):
    BOTH = "BOTH"
    PYDANTIC_ONLY = "PYDANTIC_ONLY"


class FixtureManifestEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    path: str
    contract_name: str
    schema_version: str
    python_type: str
    valid: bool
    scenario: str
    validation_scope: ValidationScope
    expected_error_code: str | None = None
    expected_error_path: str | None = None

    @model_validator(mode="after")
    def _validate_error_expectations(self) -> FixtureManifestEntry:
        if self.valid:
            if self.expected_error_code is not None:
                raise ValueError("valid fixture must not define expected_error_code")
            if self.expected_error_path is not None:
                raise ValueError("valid fixture must not define expected_error_path")
        else:
            if self.expected_error_code is None:
                raise ValueError("invalid fixture requires expected_error_code")
            if self.expected_error_path is None:
                raise ValueError("invalid fixture requires expected_error_path")
        return self


class FixtureManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    fixtures: tuple[FixtureManifestEntry, ...]


def load_manifest() -> FixtureManifest:
    return FixtureManifest.model_validate_json(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_fixture_text(path: str) -> str:
    return (FIXTURES_DIR / path).read_text(encoding="utf-8")


_SCHEMAS: dict[str, dict] = {}


def get_schemas() -> dict[str, dict]:
    if _SCHEMAS:
        return _SCHEMAS
    import tempfile

    tmpdir = Path(tempfile.mkdtemp())
    export_schemas(tmpdir)
    contracts_dir = tmpdir / "contracts"
    for schema_file in contracts_dir.glob("*.schema.json"):
        name = schema_file.name.replace(".schema.json", "")
        _SCHEMAS[name] = json.loads(schema_file.read_text(encoding="utf-8"))
    return _SCHEMAS


class TestManifestValidation:
    def test_manifest_is_valid_strict_model(self):
        manifest = load_manifest()
        assert len(manifest.fixtures) > 0

    def test_manifest_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            FixtureManifestEntry.model_validate(
                {
                    "path": "valid/x.json",
                    "contract_name": "x",
                    "schema_version": "x",
                    "python_type": "X",
                    "valid": True,
                    "scenario": "x",
                    "validation_scope": "BOTH",
                    "expected_error_code": None,
                    "expected_error_path": None,
                    "extra_field": "bad",
                }
            )

    def test_manifest_invalid_scope_rejected(self):
        with pytest.raises(ValidationError):
            FixtureManifestEntry.model_validate(
                {
                    "path": "valid/x.json",
                    "contract_name": "x",
                    "schema_version": "x",
                    "python_type": "X",
                    "valid": True,
                    "scenario": "x",
                    "validation_scope": "INVALID_SCOPE",
                    "expected_error_code": None,
                    "expected_error_path": None,
                }
            )

    def test_manifest_valid_fixture_with_error_rejected(self):
        with pytest.raises(ValidationError):
            FixtureManifestEntry.model_validate(
                {
                    "path": "valid/x.json",
                    "contract_name": "x",
                    "schema_version": "x",
                    "python_type": "X",
                    "valid": True,
                    "scenario": "x",
                    "validation_scope": "BOTH",
                    "expected_error_code": "missing",
                    "expected_error_path": "price",
                }
            )

    def test_manifest_invalid_fixture_without_error_rejected(self):
        with pytest.raises(ValidationError):
            FixtureManifestEntry.model_validate(
                {
                    "path": "invalid/x.json",
                    "contract_name": "x",
                    "schema_version": "x",
                    "python_type": "X",
                    "valid": False,
                    "scenario": "x",
                    "validation_scope": "BOTH",
                    "expected_error_code": None,
                    "expected_error_path": None,
                }
            )

    def test_manifest_matches_registry(self):
        manifest = load_manifest()
        for entry in manifest.fixtures:
            assert entry.contract_name in CONTRACT_REGISTRY, f"Unknown contract: {entry.contract_name}"
            reg = CONTRACT_REGISTRY[entry.contract_name]
            assert entry.python_type == reg.python_type.__name__, (
                f"python_type mismatch: manifest={entry.python_type}, registry={reg.python_type.__name__}"
            )
            assert entry.schema_version == entry.contract_name, (
                f"schema_version should equal contract_name: {entry.schema_version} != {entry.contract_name}"
            )

    def test_all_fixture_files_in_manifest(self):
        manifest = load_manifest()
        manifest_paths = {e.path for e in manifest.fixtures}
        actual_files: set[str] = set()
        for subdir in ("valid", "invalid"):
            subdir_path = FIXTURES_DIR / subdir
            if not subdir_path.is_dir():
                continue
            for fname in subdir_path.iterdir():
                if fname.suffix == ".json" and fname.name != "manifest.json":
                    actual_files.add(f"{subdir}/{fname.name}")
        orphan = actual_files - manifest_paths
        assert not orphan, f"Fixture files not in manifest: {orphan}"

    def test_no_orphan_manifest_entries(self):
        manifest = load_manifest()
        for entry in manifest.fixtures:
            assert (FIXTURES_DIR / entry.path).is_file(), f"Manifest references missing file: {entry.path}"

    def test_no_duplicate_paths(self):
        manifest = load_manifest()
        paths = [e.path for e in manifest.fixtures]
        assert len(paths) == len(set(paths)), f"Duplicate fixture paths: {paths}"

    def test_each_proposed_contract_has_valid_fixture(self):
        from binance_market_data_contracts.enums import ContractStatus

        manifest = load_manifest()
        proposed = [name for name, e in CONTRACT_REGISTRY.items() if e.status == ContractStatus.PROPOSED]
        contracts_with_valid = {e.contract_name for e in manifest.fixtures if e.valid}
        missing = set(proposed) - contracts_with_valid
        assert not missing, f"PROPOSED contracts without valid fixture: {missing}"

    def test_each_proposed_contract_has_invalid_fixture(self):
        from binance_market_data_contracts.enums import ContractStatus

        manifest = load_manifest()
        proposed = [name for name, e in CONTRACT_REGISTRY.items() if e.status == ContractStatus.PROPOSED]
        contracts_with_invalid = {e.contract_name for e in manifest.fixtures if not e.valid}
        missing = set(proposed) - contracts_with_invalid
        assert not missing, f"PROPOSED contracts without invalid fixture: {missing}"


class TestValidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest().fixtures if e.valid])
    def test_valid_fixture_pydantic(self, entry):
        text = load_fixture_text(entry.path)
        contract_entry = CONTRACT_REGISTRY[entry.contract_name]
        model = contract_entry.python_type
        instance = model.model_validate_json(text)
        assert instance is not None

    @pytest.mark.parametrize("entry", [e for e in load_manifest().fixtures if e.valid])
    def test_valid_fixture_json_schema(self, entry):
        schema = get_schemas().get(entry.contract_name)
        assert schema is not None, f"Schema not found for {entry.contract_name}"
        payload = json.loads(load_fixture_text(entry.path))
        if entry.validation_scope == ValidationScope.PYDANTIC_ONLY:
            return
        errors = list(Draft202012Validator(schema).iter_errors(payload))
        assert not errors, f"JSON Schema errors: {[e.message for e in errors]}"


class TestInvalidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest().fixtures if not e.valid])
    def test_invalid_fixture_pydantic_fails(self, entry):
        text = load_fixture_text(entry.path)
        contract_entry = CONTRACT_REGISTRY[entry.contract_name]
        model = contract_entry.python_type
        with pytest.raises(ValidationError) as exc_info:
            model.model_validate_json(text)
        errors = exc_info.value.errors()
        assert len(errors) > 0
        expected_code = entry.expected_error_code
        expected_path = entry.expected_error_path
        if expected_code and expected_path:
            matches = [e for e in errors if e["type"] == expected_code and _error_path_str(e) == expected_path]
            assert matches, (
                f"No error matched type='{expected_code}' path='{expected_path}'. "
                f"Got: {[(e['type'], _error_path_str(e)) for e in errors]}"
            )

    @pytest.mark.parametrize("entry", [e for e in load_manifest().fixtures if not e.valid])
    def test_invalid_fixture_json_schema(self, entry):
        schema = get_schemas().get(entry.contract_name)
        assert schema is not None, f"Schema not found for {entry.contract_name}"
        payload = json.loads(load_fixture_text(entry.path))
        errors = list(Draft202012Validator(schema).iter_errors(payload))
        if entry.validation_scope == ValidationScope.PYDANTIC_ONLY:
            assert not errors, (
                f"PYDANTIC_ONLY fixture {entry.path} should pass JSON Schema. Got errors: {[e.message for e in errors]}"
            )
        else:
            assert errors, f"Expected JSON Schema validation to fail for {entry.path}"


def _error_path_str(error: dict) -> str:
    loc = error.get("loc", ())
    return ".".join(str(p) for p in loc) if loc else "$"
