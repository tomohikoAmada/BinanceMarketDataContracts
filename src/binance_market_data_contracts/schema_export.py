"""Deterministic JSON Schema export.

Generates Draft 2020-12 JSON Schema files for all contracts in the registry.
Output is byte-stable — running twice produces identical files.

Usage:
    python -m binance_market_data_contracts.schema_export --output schemas/json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from binance_market_data_contracts.versions import CONTRACT_REGISTRY


def _make_deterministic(schema: dict[str, Any]) -> dict[str, Any]:
    schema.pop("title", None)
    if "properties" in schema:
        for prop in schema["properties"].values():
            if isinstance(prop, dict):
                prop.pop("title", None)
    return schema


def export_schemas(output_dir: Path) -> list[Path]:
    """Export all registry contracts to JSON Schema files.

    Args:
        output_dir: Target directory for schema files.

    Returns:
        List of written file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    contracts_dir = output_dir / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    schema_catalog: dict[str, Any] = {
        "contracts": {},
    }

    for name, entry in sorted(CONTRACT_REGISTRY.items()):
        model_schema = entry.python_type.model_json_schema()
        model_schema = _make_deterministic(model_schema)
        model_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        model_schema["$id"] = f"urn:binance-market-data-contracts:{name}"

        filepath = contracts_dir / f"{name}.schema.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_schema, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        written.append(filepath)

        schema_catalog["contracts"][name] = {
            "status": entry.status.value,
            "producers": list(entry.producers),
            "consumers": list(entry.consumers),
            "schema_id": model_schema["$id"],
            "filename": str(filepath.relative_to(output_dir)),
        }

    catalog_path = output_dir / "contract-catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(schema_catalog, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    written.append(catalog_path)

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export JSON Schema for all contracts")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd() / "schemas" / "json",
        help="Output directory for schema files (default: ./schemas/json)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    written = export_schemas(args.output.resolve())
    for path in sorted(written):
        print(f"  wrote: {path}")
    print(f"Exported {len(written)} files to {args.output.resolve()}")


if __name__ == "__main__":
    main()
