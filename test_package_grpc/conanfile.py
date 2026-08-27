import subprocess
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class BinanceMarketDataContractsGrpcTestPackage(ConanFile):
    test_type = "explicit"
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        CMakeDeps(self).generate()
        grpc_contracts = self.dependencies["binance-market-data-contracts-grpc-cpp"]
        base_contracts = self.dependencies["binance-market-data-contracts-cpp"]
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["BinanceMarketDataContractsGrpc_DIR"] = str(
            Path(grpc_contracts.package_folder) / "lib" / "cmake" / "BinanceMarketDataContractsGrpc"
        )
        toolchain.cache_variables["BinanceMarketDataContracts_DIR"] = str(
            Path(base_contracts.package_folder) / "lib" / "cmake" / "BinanceMarketDataContracts"
        )
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @staticmethod
    def _defined_symbols(path: Path, symbol: str) -> list[str]:
        result = subprocess.run(["nm", "-C", str(path)], text=True, capture_output=True, check=True)
        return [line for line in result.stdout.splitlines() if symbol in line and " U " not in f" {line} "]

    def test(self):
        grpc_contracts = self.dependencies["binance-market-data-contracts-grpc-cpp"]
        package_folder = Path(grpc_contracts.package_folder)
        headers = {
            path.relative_to(package_folder / "include").as_posix()
            for path in (package_folder / "include").rglob("*.pb.h")
        }
        expected_headers = {
            "binance_market_data/gateway/v1/gateway_service.pb.h",
            "binance_market_data/gateway/v1/gateway_service.grpc.pb.h",
        }
        if headers != expected_headers:
            raise RuntimeError(f"gRPC package header ownership drift: {sorted(headers)}")
        if list(package_folder.rglob("*.proto")) or list(package_folder.rglob("*.pb.cc")):
            raise RuntimeError("gRPC package contains consumer code-generation inputs")
        base_libraries = list((package_folder / "lib").glob("*binance_market_data_contracts_protobuf*"))
        if base_libraries:
            raise RuntimeError(f"gRPC package duplicated the message library: {base_libraries}")

        grpc_libraries = list((package_folder / "lib").glob("*binance_market_data_contracts_grpc*"))
        if len(grpc_libraries) != 1:
            raise RuntimeError(f"expected one gRPC library, got {grpc_libraries}")
        message_symbol = "binance_market_data::market::v1::DepthUpdate::Clear()"
        if self._defined_symbols(grpc_libraries[0], message_symbol):
            raise RuntimeError("gRPC library owns a generated message symbol")

        if can_run(self):
            executable_name = (
                "contracts_grpc_test_package.exe"
                if str(self.settings.os) == "Windows"
                else "contracts_grpc_test_package"
            )
            executable = Path(self.build_folder) / self.cpp.build.bindirs[0] / executable_name
            self.run(str(executable), env="conanrun")
            if not bool(grpc_contracts.options.get_safe("shared")):
                definitions = self._defined_symbols(executable, message_symbol)
                if len(definitions) != 1:
                    raise RuntimeError(
                        "Gateway + Projection-adapter-like final link does not have exactly one "
                        f"message symbol owner: {definitions}"
                    )
