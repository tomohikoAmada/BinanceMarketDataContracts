"""Test JSON Schema export determinism, consistency, and structure."""

import json
import os
import tempfile

from binance_market_data_contracts.schema_export import export_schemas
from binance_market_data_contracts.versions import CONTRACT_REGISTRY


def test_schema_export_deterministic():
    with tempfile.TemporaryDirectory() as tmpdir:
        first = export_schemas(tmpdir)
        second = export_schemas(tmpdir)
        assert first == second

        for path in first:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            second_path = os.path.join(tmpdir, os.path.basename(path))
            with open(second_path, encoding="utf-8") as f:
                assert content == f.read(), f"Non-deterministic output for {os.path.basename(path)}"


def test_schema_draft_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        for path in files:
            if path.endswith("__catalog__.schema.json"):
                continue
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
            assert "$schema" in schema
            assert "2020-12" in schema["$schema"]


def test_schema_has_stable_id():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        for path in files:
            if path.endswith("__catalog__.schema.json"):
                continue
            with open(path, encoding="utf-8") as f:
                schema = json.load(f)
            assert "$id" in schema
            assert "binance-market-data/" in schema["$id"]


def test_no_absolute_paths_in_schema():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        for path in files:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert "/Users/" not in content, f"Absolute path found in {os.path.basename(path)}"
            assert "\\\\" not in content, f"Backslash path found in {os.path.basename(path)}"


def test_registry_contracts_have_schemas():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        exported_names = {
            os.path.basename(p).replace(".schema.json", "") for p in files if not p.endswith("__catalog__.schema.json")
        }
        registry_names = set(CONTRACT_REGISTRY.keys())
        assert registry_names.issubset(exported_names), f"Missing schemas: {registry_names - exported_names}"


def test_catalog_has_statuses():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        catalog_path = next(p for p in files if "__catalog__" in p)
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
        for name, info in catalog["contracts"].items():
            assert "status" in info, f"Missing status in catalog for {name}"
            assert info["status"] in ("DRAFT", "PROPOSED", "ACCEPTED", "DEPRECATED", "REMOVED")


def test_schema_contains_required_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        du_path = next(p for p in files if "depth-update" in p and "__catalog__" not in p)
        with open(du_path, encoding="utf-8") as f:
            schema = json.load(f)
        required = schema.get("required", [])
        assert "metadata" in required
        assert "first_update_id" in required


def test_schema_bytes_identical_across_runs():
    with tempfile.TemporaryDirectory() as tmpdir1:
        export_schemas(tmpdir1)
        with tempfile.TemporaryDirectory() as tmpdir2:
            export_schemas(tmpdir2)
            for fname in os.listdir(tmpdir1):
                if fname.endswith(".schema.json"):
                    with open(os.path.join(tmpdir1, fname), "rb") as f:
                        content1 = f.read()
                    with open(os.path.join(tmpdir2, fname), "rb") as f:
                        content2 = f.read()
                    assert content1 == content2, f"Byte mismatch for {fname}"


def test_catalog_status_matches_registry():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_schemas(tmpdir)
        catalog_path = next(p for p in files if "__catalog__" in p)
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
        for name, info in catalog["contracts"].items():
            entry = CONTRACT_REGISTRY[name]
            assert info["status"] == entry.status.value, f"Status mismatch for {name}"
