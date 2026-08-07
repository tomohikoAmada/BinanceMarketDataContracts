from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import ClassVar

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import save
from conan.tools.scm import Git


class BinanceMarketDataContractsConan(ConanFile):
    name = "binance-market-data-contracts-cpp"
    version = "0.1.0"
    required_conan_version = ">=2.31.2 <3"
    package_type = "library"
    license = "LicenseRef-Proprietary"
    description = "Contracts-owned C++ Protobuf message package"
    settings = "os", "arch", "compiler", "build_type"
    options: ClassVar[dict[str, list[bool]]] = {"shared": [True, False], "fPIC": [True, False]}
    default_options: ClassVar[dict[str, bool]] = {"shared": False, "fPIC": True}
    exports_sources = (
        "CMakeLists.txt",
        "cmake/*",
        "tools/__init__.py",
        "tools/schema_fingerprint.py",
        "tools/verify_protoc.py",
        "tests/cpp/*",
        "tests/test_cpp_fingerprint.py",
        "src/binance_market_data_contracts/proto/*",
    )

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def requirements(self):
        # Generated public headers include the Protobuf runtime headers and the
        # exported CMake target links the runtime publicly, so both usage
        # requirements must cross the package boundary.
        self.requires(
            "protobuf/6.33.5",
            transitive_headers=True,
            transitive_libs=True,
        )

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("protobuf/6.33.5")

    def layout(self):
        cmake_layout(self)

    def export(self):
        try:
            revision = Git(self, self.recipe_folder).get_commit()
        except Exception:
            revision = "CANDIDATE_SOURCE_REVISION_UNAVAILABLE"
        save(self, Path(self.export_folder) / "contracts_source_revision.txt", revision + "\n")

    def generate(self):
        protobuf = self.dependencies["protobuf"]
        runtime_linkage = "SHARED" if bool(protobuf.options.get_safe("shared")) else "STATIC"
        if bool(protobuf.options.get_safe("lite")):
            raise ValueError("C-M4-001 requires the full Protobuf runtime, not lite")
        CMakeDeps(self).generate()
        VirtualBuildEnv(self).generate()
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["Python3_EXECUTABLE"] = sys.executable
        toolchain.cache_variables["BMD_CONTRACTS_LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        if self.options.get_safe("fPIC") is not None:
            toolchain.cache_variables["BMD_CONTRACTS_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        toolchain.cache_variables["BMD_CONTRACTS_PROTOC_PROVENANCE"] = (
            "conan:protobuf/6.33.5#ca5ff466767b31a1b496ec60247e105c"
        )
        toolchain.cache_variables["BMD_CONTRACTS_PROTOBUF_RREV"] = "ca5ff466767b31a1b496ec60247e105c"
        toolchain.cache_variables["BMD_CONTRACTS_PROTOBUF_RUNTIME_LINKAGE"] = runtime_linkage
        revision_file = Path(self.recipe_folder) / "contracts_source_revision.txt"
        if revision_file.is_file():
            revision = revision_file.read_text(encoding="utf-8").strip()
        else:
            try:
                revision = Git(self, self.source_folder).get_commit()
            except Exception:
                revision = os.environ.get("BMD_CONTRACTS_SOURCE_REVISION", "CANDIDATE_SOURCE_REVISION_UNAVAILABLE")
        toolchain.cache_variables["BinanceMarketDataContracts_CONTRACTS_SOURCE_REVISION"] = revision
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.ctest()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # This package installs its own component-aware config with canonical
        # metadata. Do not let CMakeDeps shadow it with a generated config.
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "BinanceMarketDataContracts")
        component = self.cpp_info.components["Protobuf"]
        component.libs = ["binance_market_data_contracts_protobuf"]
        component.requires = ["protobuf::libprotobuf"]
        component.set_property("cmake_target_name", "BinanceMarketDataContracts::Protobuf")
        self.cpp_info.builddirs.append("lib/cmake/BinanceMarketDataContracts")
