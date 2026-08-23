from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import ClassVar

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Git


class BinanceMarketDataContractsGrpcConan(ConanFile):
    name = "binance-market-data-contracts-grpc-cpp"
    version = "0.1.0"
    required_conan_version = ">=2.31.2 <3"
    package_type = "library"
    license = "LicenseRef-Proprietary"
    description = "Contracts-owned C++ Gateway service and gRPC stub package"
    settings = "os", "arch", "compiler", "build_type"
    options: ClassVar[dict[str, list[bool]]] = {"shared": [True, False], "fPIC": [True, False]}
    default_options: ClassVar[dict[str, bool]] = {
        "shared": False,
        "fPIC": True,
        "grpc/*:shared": False,
        "grpc/*:codegen": False,
        "grpc/*:cpp_plugin": False,
        "grpc/*:csharp_ext": False,
        "grpc/*:csharp_plugin": False,
        "grpc/*:node_plugin": False,
        "grpc/*:objective_c_plugin": False,
        "grpc/*:php_plugin": False,
        "grpc/*:python_plugin": False,
        "grpc/*:ruby_plugin": False,
        "grpc/*:otel_plugin": False,
    }
    default_build_options: ClassVar[dict[str, bool]] = {
        "grpc/*:shared": False,
        "grpc/*:codegen": True,
        "grpc/*:cpp_plugin": True,
        "grpc/*:csharp_ext": False,
        "grpc/*:csharp_plugin": False,
        "grpc/*:node_plugin": False,
        "grpc/*:objective_c_plugin": False,
        "grpc/*:php_plugin": False,
        "grpc/*:python_plugin": False,
        "grpc/*:ruby_plugin": False,
        "grpc/*:otel_plugin": False,
    }
    exports_sources = (
        "grpc/CMakeLists.txt",
        "grpc/BinanceMarketDataContractsGrpcConfig.cmake.in",
        "grpc/provenance.json.in",
        "cmake/ContractsMetadata.cmake",
        "tools/verify_grpc_cpp_plugin.py",
        "tools/verify_protoc.py",
        "tests/cpp/grpc_tests.cpp",
        "src/binance_market_data_contracts/proto/*",
    )

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires(
            "binance-market-data-contracts-cpp/0.1.0",
            transitive_headers=True,
            transitive_libs=True,
        )
        self.requires(
            "grpc/1.83.0",
            transitive_headers=True,
            transitive_libs=True,
        )

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        linkage = bool(self.options.shared)
        self.options["binance-market-data-contracts-cpp"].shared = linkage
        self.options["grpc"].shared = linkage
        for option in (
            "codegen",
            "cpp_plugin",
            "csharp_ext",
            "csharp_plugin",
            "node_plugin",
            "objective_c_plugin",
            "php_plugin",
            "python_plugin",
            "ruby_plugin",
            "otel_plugin",
        ):
            setattr(self.options["grpc"], option, False)

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("protobuf/6.33.5")
        self.tool_requires("grpc/1.83.0")

    def layout(self):
        cmake_layout(self)

    def export(self):
        git = Git(self, self.recipe_folder)
        revision = git.get_commit()
        if git.is_dirty():
            raise ValueError("Conan export requires a clean Contracts Git worktree")
        injected = os.environ.get("BMD_CONTRACTS_SOURCE_REVISION")
        if injected is not None and injected != revision:
            raise ValueError("BMD_CONTRACTS_SOURCE_REVISION does not match the exported Contracts Git HEAD")

    @staticmethod
    def _recipe_revision(dependency, label: str) -> str:
        revision = getattr(dependency.ref, "revision", None) or getattr(dependency, "recipe_revision", None)
        if not revision:
            raise ValueError(f"Unable to resolve the locked {label} recipe revision")
        return str(revision)

    def generate(self):
        base = self.dependencies["binance-market-data-contracts-cpp"]
        grpc_runtime = self.dependencies["grpc"]
        protobuf_tool = self.dependencies.build["protobuf"]
        grpc_tool = self.dependencies.build["grpc"]

        base_rrev = self._recipe_revision(base, "base Contracts")
        grpc_runtime_rrev = self._recipe_revision(grpc_runtime, "host gRPC")
        grpc_tool_rrev = self._recipe_revision(grpc_tool, "build-context gRPC")
        protobuf_tool_rrev = self._recipe_revision(protobuf_tool, "build-context Protobuf")
        if grpc_runtime_rrev != grpc_tool_rrev:
            raise ValueError("Host and build-context gRPC recipe revisions differ")
        if protobuf_tool_rrev != "ca5ff466767b31a1b496ec60247e105c":
            raise ValueError("Build-context Protobuf recipe revision drift")

        executable_suffix = ".exe" if str(self.settings_build.os) == "Windows" else ""
        protoc = Path(protobuf_tool.package_folder) / "bin" / f"protoc{executable_suffix}"
        grpc_plugin = Path(grpc_tool.package_folder) / "bin" / f"grpc_cpp_plugin{executable_suffix}"
        runtime_linkage = "SHARED" if bool(grpc_runtime.options.get_safe("shared")) else "STATIC"

        CMakeDeps(self).generate()
        VirtualBuildEnv(self).generate()
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["Python3_EXECUTABLE"] = sys.executable
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        if self.options.get_safe("fPIC") is not None:
            toolchain.cache_variables["BMD_CONTRACTS_GRPC_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_PROTOC_EXECUTABLE"] = str(protoc)
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_PROTOC_PROVENANCE"] = (
            f"conan:protobuf/6.33.5#{protobuf_tool_rrev}"
        )
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_PROTOBUF_RREV"] = protobuf_tool_rrev
        toolchain.cache_variables["BinanceMarketDataContracts_DIR"] = str(
            Path(base.package_folder) / "lib" / "cmake" / "BinanceMarketDataContracts"
        )
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_CPP_PLUGIN_EXECUTABLE"] = str(grpc_plugin)
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_CPP_PLUGIN_PACKAGE_FOLDER"] = str(Path(grpc_tool.package_folder))
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_CPP_PLUGIN_PROVENANCE"] = f"conan:grpc/1.83.0#{grpc_tool_rrev}"
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_RREV"] = grpc_tool_rrev
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_BASE_RREV"] = base_rrev
        toolchain.cache_variables["BMD_CONTRACTS_GRPC_RUNTIME_LINKAGE"] = runtime_linkage

        revision = os.environ.get("BMD_CONTRACTS_SOURCE_REVISION")
        if revision is None:
            try:
                git = Git(self, self.source_folder)
                revision = git.get_commit()
                if git.is_dirty():
                    raise ValueError("Contracts source provenance cannot describe a dirty worktree")
            except Exception as exc:
                raise ValueError("BMD_CONTRACTS_SOURCE_REVISION is required when building an exported recipe") from exc
        if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision):
            raise ValueError("Contracts source revision must be a lowercase 40-character Git SHA")
        toolchain.cache_variables["BinanceMarketDataContractsGrpc_CONTRACTS_SOURCE_REVISION"] = revision
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="grpc")
        cmake.build()
        cmake.ctest()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "BinanceMarketDataContractsGrpc")
        component = self.cpp_info.components["Grpc"]
        component.libs = ["binance_market_data_contracts_grpc"]
        component.requires = [
            "binance-market-data-contracts-cpp::Protobuf",
            "grpc::grpc++",
        ]
        component.set_property("cmake_target_name", "BinanceMarketDataContracts::Grpc")
        self.cpp_info.builddirs.append("lib/cmake/BinanceMarketDataContractsGrpc")
