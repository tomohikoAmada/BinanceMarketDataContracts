import pytest

from tools.verify_conan_graph_boundaries import verify_base_graph, verify_grpc_graph


def _node(reference: str, context: str, **options: bool):
    return {
        "ref": reference + "#revision",
        "context": context,
        "options": {key: str(value) for key, value in options.items()},
    }


def _grpc_options(*, codegen: bool, cpp_plugin: bool):
    return {
        "codegen": codegen,
        "cpp_plugin": cpp_plugin,
        "csharp_ext": False,
        "csharp_plugin": False,
        "node_plugin": False,
        "objective_c_plugin": False,
        "php_plugin": False,
        "python_plugin": False,
        "ruby_plugin": False,
        "otel_plugin": False,
    }


def test_base_graph_rejects_grpc_in_any_context():
    verify_base_graph([_node("protobuf/6.33.5", "host")])
    with pytest.raises(RuntimeError, match="contains gRPC"):
        verify_base_graph([_node("grpc/1.83.0", "build")])


def test_base_graph_requires_matching_protobuf_linkage():
    with pytest.raises(RuntimeError, match="drive Protobuf linkage"):
        verify_base_graph(
            [
                _node("binance-market-data-contracts-cpp/0.1.0", "host", shared=True),
                _node("protobuf/6.33.5", "host", shared=False),
            ]
        )


def test_grpc_graph_requires_one_base_and_minimal_context_options():
    nodes = [
        _node("binance-market-data-contracts-cpp/0.1.0", "host", shared=False),
        _node("binance-market-data-contracts-grpc-cpp/0.1.0", "host", shared=False),
        _node(
            "grpc/1.83.0",
            "host",
            shared=False,
            **_grpc_options(codegen=False, cpp_plugin=False),
        ),
        _node(
            "grpc/1.83.0",
            "build",
            shared=False,
            **_grpc_options(codegen=True, cpp_plugin=True),
        ),
    ]
    verify_grpc_graph(nodes)


def test_grpc_graph_rejects_unrelated_build_plugin():
    build_options = _grpc_options(codegen=True, cpp_plugin=True)
    build_options["python_plugin"] = True
    nodes = [
        _node("binance-market-data-contracts-cpp/0.1.0", "host", shared=False),
        _node(
            "grpc/1.83.0",
            "host",
            shared=False,
            **_grpc_options(codegen=False, cpp_plugin=False),
        ),
        _node("grpc/1.83.0", "build", shared=False, **build_options),
    ]
    with pytest.raises(RuntimeError, match="python_plugin"):
        verify_grpc_graph(nodes)
