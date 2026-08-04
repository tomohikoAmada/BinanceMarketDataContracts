"""Test golden fixtures: valid pass, invalid fail, manifest consistency."""

import json
import os

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.versions import CONTRACT_REGISTRY

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_fixture(path: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, path), encoding="utf-8") as f:
        return json.load(f)


def load_manifest() -> dict:
    with open(os.path.join(FIXTURES_DIR, "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


class TestValidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if e["valid"]])
    def test_valid_fixture(self, entry):
        payload = load_fixture(entry["path"])
        contract_entry = CONTRACT_REGISTRY.get(entry["contract_name"])
        assert contract_entry is not None, f"Contract {entry['contract_name']} not in registry"
        model = contract_entry.python_type
        instance = model.model_validate(payload)
        assert instance is not None


class TestInvalidFixtures:
    @pytest.mark.parametrize("entry", [e for e in load_manifest()["fixtures"] if not e["valid"]])
    def test_invalid_fixture(self, entry):
        payload = load_fixture(entry["path"])
        contract_entry = CONTRACT_REGISTRY.get(entry["contract_name"])
        assert contract_entry is not None, f"Contract {entry['contract_name']} not in registry"
        model = contract_entry.python_type
        with pytest.raises(ValidationError) as exc_info:
            model.model_validate(payload)
        errors = exc_info.value.errors()
        error_paths = [".".join(str(p) for p in e["loc"]) for e in errors]
        assert len(errors) > 0
        if entry.get("expected_error_path"):
            found = any(entry["expected_error_path"] in ep for ep in error_paths)
            assert found, f"Expected error at '{entry['expected_error_path']}', got paths: {error_paths}"


class TestManifestCoverage:
    def test_all_fixture_files_in_manifest(self):
        manifest = load_manifest()
        manifest_paths = {e["path"] for e in manifest["fixtures"]}
        actual_files = set()
        for subdir in ("valid", "invalid"):
            subdir_path = os.path.join(FIXTURES_DIR, subdir)
            if not os.path.isdir(subdir_path):
                continue
            for fname in os.listdir(subdir_path):
                if fname.endswith(".json"):
                    actual_files.add(f"{subdir}/{fname}")
        orphan = actual_files - manifest_paths
        assert not orphan, f"Fixture files not in manifest: {orphan}"

    def test_no_orphan_manifest_entries(self):
        manifest = load_manifest()
        for entry in manifest["fixtures"]:
            full_path = os.path.join(FIXTURES_DIR, entry["path"])
            assert os.path.isfile(full_path), f"Manifest references missing file: {entry['path']}"

    def test_each_proposed_contract_has_valid_fixture(self):
        manifest = load_manifest()
        from binance_market_data_contracts.enums import ContractStatus

        proposed_contracts = [name for name, e in CONTRACT_REGISTRY.items() if e.status == ContractStatus.PROPOSED]
        contracts_with_valid = {e["contract_name"] for e in manifest["fixtures"] if e["valid"]}
        missing = set(proposed_contracts) - contracts_with_valid
        assert not missing, f"PROPOSED contracts without valid fixture: {missing}"
