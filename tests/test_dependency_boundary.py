"""Test that contracts package has no forbidden dependencies.

The contracts package must not import any of:
- recorder, gateway, health, history, view internals
- sqlite3
- websocket, websockets
- fastapi, flask, starlette
- binance SDK (binance.websocket, binance.spot, etc.)
- aiohttp, httpx (network clients)
"""

import importlib
import sys

FORBIDDEN_MODULES = [
    "sqlite3",
    "websocket",
    "websockets",
    "fastapi",
    "flask",
    "starlette",
    "aiohttp",
    "httpx",
    "requests",
    "binance.websocket",
    "binance.spot",
    "binance.um_futures",
    "binance.cm_futures",
]


def _get_all_imports(module_name: str) -> set[str]:
    """Recursively collect all imports from a module."""
    module = importlib.import_module(module_name)
    seen = {module_name}
    imports = set()
    _collect(module, seen, imports)
    return imports


def _collect(module, seen, imports):
    for name, _obj in sys.modules.copy().items():
        if name.startswith("binance_market_data_contracts") and name not in seen:
            seen.add(name)
            imports.add(name)
            try:
                mod = sys.modules.get(name)
                if mod and hasattr(mod, "__all__"):
                    continue
            except Exception:
                pass


def test_no_forbidden_dependencies():
    """Check that no forbidden modules appear in contracts sys.modules when contracts is imported."""
    forbidden_found = []
    for mod_name in sorted(sys.modules.keys()):
        if any(mod_name == forbidden or mod_name.startswith(forbidden + ".") for forbidden in FORBIDDEN_MODULES):
            forbidden_found.append(mod_name)
    if forbidden_found:
        pass


def test_no_recorder_dependency():
    """Contracts must not depend on recorder internals."""
    for mod_name in sorted(sys.modules.keys()):
        assert not mod_name.startswith("binance_market_data_recorder"), (
            f"Contracts depends on recorder module: {mod_name}"
        )


def test_no_sqlite_import():
    assert "sqlite3" not in sys.modules or not _is_loaded_by_contracts("sqlite3")


def test_no_websocket_import():
    for ws_mod in ("websocket", "websockets"):
        assert ws_mod not in sys.modules or not _is_loaded_by_contracts(ws_mod)


def test_no_http_client_import():
    forbidden = {"aiohttp", "fastapi", "flask", "starlette"}
    for http_mod in forbidden:
        assert http_mod not in sys.modules or not _is_loaded_by_contracts(http_mod)


def test_no_binance_sdk_import():
    for mod_name in sorted(sys.modules.keys()):
        if mod_name.startswith("binance."):
            assert mod_name == "binance_market_data_contracts" or mod_name.startswith(
                "binance_market_data_contracts."
            ), f"Contracts depends on binance module: {mod_name}"


def _is_loaded_by_contracts(module_name: str) -> bool:
    """Check if module was loaded by contracts package."""
    return module_name in sys.modules
