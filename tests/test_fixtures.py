"""Test golden fixtures: Pydantic + JSON Schema validation.

Uses jsonschema library to validate fixtures against generated schemas.
Fixtures that pass only Pydantic semantic checks are marked PYDANTIC_ONLY.
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.schema_export import export_schemas
from binance_market_data_contracts.versions import CONTRACT_REGISTRY

try:
    from jsonschema import Draft202012Validator

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    Draft202012Validator = None  # type: ignore

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"


def load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_fixture_text(path: str) -> str:
    with open(FIXTURES_DIR / path, encoding="utf-8") as f:
        return f.read()


_SCHEMAS_DIR = None
_SCHEMAS = {}


def get_schemas():
    global _SCHEMAS_DIR, _SCHEMAS
    if _SCHEMAS:
        return _SCHEMAS
    import tempfile

    _SCHEMAS_DIR = tempfile.mkdtemp()
    export_schemas(Path(_SCHEMAS_DIR))
    contracts_dir = Path(_SCHEMAS_DIR) / "contracts"
    for schema_file in contracts_dir.glob("*.schema.json"):
        name = schema_file.stem.replace(".schema", "")
        with open(schema_file, encoding="utf-8") as f:
            _SCHEMAS[name] = json.load(f)
    return _SCHEMAS


class TestValidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if e["valid"]])
    def test_valid_fixture_pydantic(self, entry):
        text = load_fixture_text(entry["path"])
        contract_entry = CONTRACT_REGISTRY[entry["contract_name"]]
        model = contract_entry.python_type
        instance = model.model_validate_json(text)
        assert instance is not None

    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if e["valid"]])
    def test_valid_fixture_json_schema(self, entry):
        if not HAS_JSONSCHEMA:
            pytest.skip("jsonschema not installed")
        schema = get_schemas().get(entry["contract_name"])
        if schema is None:
            pytest.skip(f"Schema not found for {entry['contract_name']}")
        payload = json.loads(load_fixture_text(entry["path"]))
        validator_cls = Draft202012Validator(schema)
        errors = list(validator_cls.iter_errors(payload))
        if entry.get("validation_scope") == "PYDANTIC_ONLY":
            return
        assert not errors, f"JSON Schema errors: {[e.message for e in errors]}"


class TestInvalidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if not e["valid"]])
    def test_invalid_fixture_pydantic_fails(self, entry):
        text = load_fixture_text(entry["path"])
        contract_entry = CONTRACT_REGISTRY[entry["contract_name"]]
        model = contract_entry.python_type
        with pytest.raises(ValidationError) as exc_info:
            model.model_validate_json(text)
        errors = exc_info.value.errors()
        assert len(errors) > 0

        expected_code = entry.get("expected_error_code")
        expected_path = entry.get("expected_error_path")
        if expected_code and expected_path:
            matches = [e for e in errors if e["type"] == expected_code and _error_path_str(e) == expected_path]
            assert matches, (
                f"No error matched type='{expected_code}' path='{expected_path}'. "
                f"Got: {[(e['type'], _error_path_str(e)) for e in errors]}"
            )

    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if not e["valid"]])
    def test_invalid_fixture_json_schema(self, entry):
        if not HAS_JSONSCHEMA:
            pytest.skip("jsonschema not installed")
        if entry.get("validation_scope") == "PYDANTIC_ONLY":
            pytest.skip("PYDANTIC_ONLY semantics not in JSON Schema")
        schema = get_schemas().get(entry["contract_name"])
        if schema is None:
            pytest.skip(f"Schema not found for {entry['contract_name']}")
        payload = json.loads(load_fixture_text(entry["path"]))
        validator_cls = Draft202012Validator(schema)
        errors = list(validator_cls.iter_errors(payload))
        assert errors, f"Expected JSON Schema validation to fail for {entry['path']}"


class TestManifestCoverage:
    def test_all_fixture_files_in_manifest(self):
        manifest = load_manifest()
        manifest_paths = {e["path"] for e in manifest["fixtures"]}
        actual_files = set()
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
        for entry in manifest["fixtures"]:
            full_path = FIXTURES_DIR / entry["path"]
            assert full_path.is_file(), f"Manifest references missing file: {entry['path']}"

    def test_each_proposed_contract_has_valid_fixture(self):
        from binance_market_data_contracts.enums import ContractStatus

        manifest = load_manifest()
        proposed_contracts = [name for name, e in CONTRACT_REGISTRY.items() if e.status == ContractStatus.PROPOSED]
        contracts_with_valid = {e["contract_name"] for e in manifest["fixtures"] if e["valid"]}
        missing = set(proposed_contracts) - contracts_with_valid
        assert not missing, f"PROPOSED contracts without valid fixture: {missing}"


def _error_path_str(error: dict) -> str:
    loc = error.get("loc", ())
    return ".".join(str(p) for p in loc) if loc else "$"
