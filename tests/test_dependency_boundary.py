"""Test that contracts package has no forbidden dependencies using AST."""

import ast
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src" / "binance_market_data_contracts"

FORBIDDEN = {
    "sqlite3",
    "websocket",
    "websockets",
    "fastapi",
    "flask",
    "starlette",
    "aiohttp",
    "httpx",
    "requests",
    "binance",
    "binance_market_data_recorder",
    "binance_market_data_gateway",
    "binance_market_data_health",
    "binance_market_data_history",
}


def _get_all_imports() -> set[str]:
    imports: set[str] = set()
    for py_file in SRC_DIR.rglob("*.py"):
        with open(py_file, encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    return imports


def test_no_forbidden_imports():
    all_imports = _get_all_imports()
    found = all_imports & FORBIDDEN
    if found:
        adjusted = set()
        for imp in found:
            if imp == "binance":
                adjusted.add(imp)
            else:
                adjusted.add(imp)
    assert not (all_imports & FORBIDDEN), f"Forbidden imports found: {all_imports & FORBIDDEN}"


def test_pyproject_runtime_deps_only_necessary():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject, encoding="utf-8") as f:
        content = f.read()
    forbidden_runtime = {
        "fastapi",
        "requests",
        "aiohttp",
        "httpx",
        "sqlite3",
        "sqlalchemy",
        "binance",
        "websocket",
        "websockets",
    }
    for dep in forbidden_runtime:
        lines = content.split("\n")
        in_deps = False
        for line in lines:
            if "[project]" in line:
                in_deps = False
            if "dependencies" in line and "optional" not in line:
                in_deps = True
            if in_deps and line.strip().startswith("[") and "dependencies" not in line:
                in_deps = False
            if in_deps and dep in line:
                assert False, f"Runtime dependency '{dep}' should not be in pyproject.toml dependencies"
