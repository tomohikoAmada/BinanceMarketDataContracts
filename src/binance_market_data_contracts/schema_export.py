"""Deterministic JSON Schema export.

Generates Draft 2020-12 JSON Schema files for all contracts in the registry.
Output is byte-stable — running twice produces identical files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from binance_market_data_contracts.versions import CONTRACT_REGISTRY


def _make_deterministic(schema: dict[str, Any]) -> dict[str, Any]:
    """Remove non-deterministic fields and normalize schema."""
    schema.pop("title", None)
    if "properties" in schema:
        for prop in schema["properties"].values():
            if isinstance(prop, dict):
                prop.pop("title", None)
    return schema


def export_schemas(output_dir: str, indent: int = 2) -> list[str]:
    """Export all registry contracts to JSON Schema files.

    Returns the list of written file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    schema_catalog: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "BinanceMarketData Contract Schema Catalog",
        "description": "Auto-generated schema catalog. Do not edit manually.",
        "contracts": {},
    }

    for name, entry in sorted(CONTRACT_REGISTRY.items()):
        model_schema = entry.python_type.model_json_schema()
        model_schema = _make_deterministic(model_schema)
        model_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        model_schema["$id"] = f"binance-market-data/{name}.schema.json"

        filename = f"{name}.schema.json"
        filepath = out / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_schema, f, indent=indent, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        written.append(str(filepath))

        schema_catalog["contracts"][name] = {
            "status": entry.status.value,
            "producer": entry.producer,
            "consumer": entry.consumer,
            "schema_id": model_schema["$id"],
            "filename": filename,
        }

    catalog_path = out / "__catalog__.schema.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(schema_catalog, f, indent=indent, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    written.append(str(catalog_path))

    return written


def main() -> None:
    """CLI entry point for schema export."""
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "schemas" / "json"
    written = export_schemas(str(output_dir))
    for path in written:
        print(f"  wrote: {os.path.relpath(path, repo_root)}")
    print(f"Exported {len(written)} files to {output_dir}")


if __name__ == "__main__":
    main()
