from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class BinanceMarketDataContractsTestPackage(ConanFile):
    test_type = "explicit"
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        CMakeDeps(self).generate()
        dependency = self.dependencies["binance-market-data-contracts-cpp"]
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["BinanceMarketDataContracts_DIR"] = str(
            Path(dependency.package_folder) / "lib" / "cmake" / "BinanceMarketDataContracts"
        )
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(self.cpp.build.bindirs[0] + "/contracts_test_package", env="conanrun")
