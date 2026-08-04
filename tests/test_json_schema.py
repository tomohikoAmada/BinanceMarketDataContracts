"""Test JSON Schema export determinism, consistency, and structure."""

import json
import tempfile
from pathlib import Path

from binance_market_data_contracts.schema_export import export_schemas
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


def test_schema_export_deterministic():
    with tempfile.TemporaryDirectory() as tmpdir1:
        first = export_schemas(Path(tmpdir1))
        with tempfile.TemporaryDirectory() as tmpdir2:
            second = export_schemas(Path(tmpdir2))
            first_names = sorted(p.name for p in first)
            second_names = sorted(p.name for p in second)
            assert first_names == second_names


def test_schema_draft_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        for path in files:
            if path.name.startswith("contract-catalog"):
                continue
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
            assert "2020-12" in schema.get("$schema", "")


def test_schema_has_stable_urn():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        for path in files:
            if path.name.startswith("contract-catalog"):
                continue
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
            assert "$id" in schema
            assert schema["$id"].startswith("urn:binance-market-data-contracts:")


def test_no_absolute_paths_in_schema():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        for path in files:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert "/Users/" not in content
            assert "\\home\\" not in content.lower()


def test_registry_contracts_exact_match_exported():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        exported_names: set[str] = set()
        for p in files:
            if "catalog" in p.name:
                continue
            name = p.name.replace(".schema.json", "")
            exported_names.add(name)
        registry_names = set(CONTRACT_REGISTRY.keys())
        assert registry_names == exported_names, (
            f"Mismatch: registry {registry_names - exported_names}, extra: {exported_names - registry_names}"
        )


def test_catalog_has_statuses():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        catalog_path = next(p for p in files if "catalog" in p.name)
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
        for name, info in catalog["contracts"].items():
            assert "status" in info
            assert info["status"] in ("DRAFT", "PROPOSED", "ACCEPTED", "DEPRECATED", "REMOVED")


def test_schema_contains_required_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        du_path = next(p for p in files if "depth-update" in p.name)
        with open(du_path, encoding="utf-8") as f:
            schema = json.load(f)
        required = schema.get("required", [])
        assert "metadata" in required


def test_schema_bytes_identical_across_runs():
    with tempfile.TemporaryDirectory() as tmpdir1:
        export_schemas(Path(tmpdir1))
        with tempfile.TemporaryDirectory() as tmpdir2:
            export_schemas(Path(tmpdir2))
            contracts1 = Path(tmpdir1) / "contracts"
            contracts2 = Path(tmpdir2) / "contracts"
            for fname in sorted(contracts1.iterdir()):
                f2 = contracts2 / fname.name
                assert f2.is_file(), f"Missing: {fname.name}"
                assert fname.read_bytes() == f2.read_bytes(), f"Byte mismatch for {fname.name}"


def test_decimal_pattern_in_schema():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        du_path = next(p for p in files if "depth-update" in p.name)
        with open(du_path, encoding="utf-8") as f:
            schema = json.load(f)
        schema_str = json.dumps(schema)
        pattern = r"^(0|[1-9][0-9]*)(\.[0-9]+)?$"
        assert pattern.replace("\\", "") in schema_str.replace("\\", "")


def test_identifier_constraints_in_schema():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(Path(tmpdir))
        bt_path = next(p for p in files if "book-ticker" in p.name)
        with open(bt_path, encoding="utf-8") as f:
            schema = json.load(f)
        schema_str = json.dumps(schema)
        assert "minLength" in schema_str, "Schema should contain minLength for identifiers"
