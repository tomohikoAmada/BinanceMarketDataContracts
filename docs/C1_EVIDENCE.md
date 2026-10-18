# Contracts C1 evidence

2026-10-18 · C1 implementation, fixed-dependency offline validation and independent
review complete. Delivery is tracked by [PR #23](https://github.com/tomohikoAmada/BinanceMarketDataContracts/pull/23);
the PR records its exact-head CI and final merge state.
All six sibling Milestone Plan documents were read. Scope is C1 under BMD-2,
including preserving and committing the pre-existing C0 prerequisite; no C2
optimization, runtime expansion, Recorder/VPS changes or package publication.

- [x] Preserve C0 source as `db8156f1e16ba7a4a5ee8d5b26316139b7e218f3` on `codex/contracts-c1`.
- [x] Verify actual Gateway source/support and fixed binary graph; export Projection
  source `555dd1f4d846e19cfd6fbe55676c86504559048e` to reproduce existing RREV `d95fa71d6dca8d931e72fbb5b74114a9`.
- [x] Document five market/book models, eight RPC-related models, StreamStatus/helpers,
  current three RPCs and unsupported MarketState in [consumer page](contracts/current-capabilities.md).
- [x] Contracts validation and schema/codegen/descriptor compatibility.
- [x] Fixed Gateway production build/RPC integration and Projection replay/adapter checks.
- [x] Independent subagent code/document review: no actionable findings.
- [x] Reviewable commits pushed and [PR #23](https://github.com/tomohikoAmada/BinanceMarketDataContracts/pull/23) opened; inspect that PR for live CI/merge state.

## Concrete binary graph

Read from Gateway `build/g7-conan/graph.json` and installed provenance; macOS
armv8 / AppleClang 21 / libc++ / C++20 / Release, static, fPIC=True.
These package IDs/PREVs identify this tested platform, not portable binary IDs.

| Package (RREV in consumer page) | Package ID | PREV |
| --- | --- | --- |
| Contracts messages | `a1a286da6ca09b590d78bcb14d8250c025131c29` | `3ed98b3377f27e55f4be6ba8b86e0820` |
| Contracts gRPC | `3acd5bb035736877e698472136645086258451a7` | `a26249bb7524196e6f0f5dedc341b57d` |
| Projection, proto_adapter=True | `cb502a97da45967059ab2838b16d0fa48417c4a7` | `22ae52ec93b6a59c9c5e7536cacfd7c6` |

The installed message and gRPC provenance names source
`518880bdfa60948c3b65b6b3525d024526995166`. This is deliberately distinct from the
new Python/JSON C0 source. Recipe/export and descriptor checks establish that
the bounded Domain correction does not require replacing these binaries.

## Validation

Local macOS arm64, AppleClang 21, CMake 4.3.2, Conan 2.31.2. Python checks used
repository `.venv`: Python 3.14.6, Pydantic 2.13.4, protobuf 6.33.5,
grpcio/grpcio-tools 1.81.1, pytest 9.1.1. These are validation-environment versions,
not a newly published Python dependency lock.

| Check | Result | Ignored local log/output |
| --- | --- | --- |
| Ruff lint / format, mypy, diff whitespace | PASS (17 typed source files) | commands below |
| Full Domain/adapter/fixture/schema tests with descriptor + locked protoc identity | **675 passed, 0 skipped**, 3.26s | Contracts `build/c1/pytest-with-protoc.log` |
| JSON Schema re-export, Python codegen check | PASS, byte-identical to committed outputs | Contracts `build/c1/schemas/` |
| Buf format/lint/breaking vs main and descriptor fingerprint | PASS; unchanged fingerprint in consumer page | Contracts `build/c1/descriptor.pb` |
| Contracts C++ message build/semantic/metadata/fingerprint | **2/2 PASS**, 0.57s | Contracts `build/c1/cpp-{configure,build,ctest}.log` |
| Python wheel/sdist build + twine | PASS; local artifacts only | Contracts `build/c1/python-build.log`, `twine.log`, `dist/` |
| Gateway fresh Release production graph, including bmd-gatewayd | **22/22 PASS**, 13.40s | Gateway `build/contracts-c1/gateway-{configure,build,ctest}.log` |
| Projection pinned source, Core+ProtoAdapter build | PASS; source export reproduces selected RREV | Gateway `build/contracts-c1/projection-{export,configure,build}.log` |
| Projection Spot/USD-M sequence, replay fixture/parser, property/allocation, metadata/lock checks | **58/58 PASS** | Gateway `build/contracts-c1/projection-ctest.log` |
| Projection actual adapter differential/fixture replay and snapshot extraction | **50/50 PASS** | Gateway `build/contracts-c1/projection-adapter-replay-ctest.log` |
| Projection wire admission, exact Symbol, depth limits, known-fixture round-trip and snapshot output | **21/21 PASS** | Gateway `build/contracts-c1/projection-wire-ctest.log` |
| Gateway `scripts/format-check.sh` | PASS | Gateway `build/contracts-c1/gateway-format.log` |
| Conan lock creation against each committed lock + identity comparison | PASS for message and gRPC graphs; OpenSSL stays 3.6.4 | Contracts `build/c1/{base,grpc}-lock-replay.log` |

C0/C1 leave all C++ export inputs unchanged against Contracts main `8701c330`:
recipes, cmake, proto/generated Python, C++ tests/tools and both Conan locks.
The C++ build initially found system libprotoc 35.0 and rejected it; explicitly
selecting cached locked libprotoc 33.5 resolved configuration, with no source or
pin change. After the clean documentation commit `abc1d97`, both Contracts exports also
reproduced their original RREVs (`build/c1/message-export.log`, `grpc-export.log`).
No dependencies were cold-built locally, and no acceptance hook was added.
No C++ runtime/concurrency change was made, so no new sanitizer matrix was
needed; Gateway G1's existing sanitizer evidence is not re-labelled as C1 work.

Gateway tests exercise parser → Projection → loopback Book/Event/Status,
including shared USD-M time oracles, negotiation/admission, generation/presence,
Applied-only book updates and recovery/slow-client isolation. They validate the
existing implementation and pinned combination; they do not close G2 four-product
production/CI or G3 VPS/API/performance delivery. Projection tests use an archive
of fixed main `555dd1f4`, not the unrelated local P0 work branch.

Reproduction (from the appropriate repository):

```sh
# Contracts; Python environment is the existing repository .venv.
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src/binance_market_data_contracts
buf build --as-file-descriptor-set -o build/c1/descriptor.pb
# Set BMD_DESCRIPTOR_SET, BMD_PROTO_ROOT, BMD_PROTOC_EXECUTABLE,
# BMD_PROTOC_VERSION and BMD_PROTOC_PROVENANCE as CMake does for
# fingerprint_algorithm to include its generator-identity tests.
.venv/bin/pytest -q -ra
.venv/bin/python -m binance_market_data_contracts.schema_export --output build/c1/schemas
diff -ru schemas/json build/c1/schemas
.venv/bin/python -m binance_market_data_contracts.proto_codegen --check
buf format --diff --exit-code
buf lint
buf breaking --against '.git#ref=main'
.venv/bin/python -m tools.schema_fingerprint --descriptor-set build/c1/descriptor.pb

# Gateway: reuse exact cached binary graph, explicitly enable production.
cmake -S . -B build/contracts-c1/gateway -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/build/g7-conan/conan_toolchain.cmake" \
  -DCMAKE_OSX_SYSROOT=macosx -DBMD_GATEWAY_BUILD_PRODUCTION_DAEMON=ON \
  -DBMD_GATEWAY_BUILD_G2_SYNTHETIC_HOST=ON \
  -DBMD_GATEWAY_BUILD_G8_INTEGRATION_ACCEPTANCE=ON -DBMD_GATEWAY_BUILD_TESTS=ON
cmake --build build/contracts-c1/gateway --parallel 4
ctest --test-dir build/contracts-c1/gateway --output-on-failure
bash scripts/format-check.sh
```

Projection archive configuration used its existing fixed-dependency toolchain
`build/independent-review-20261011/deps/build/Release/generators/conan_toolchain.cmake`,
explicit ProtoAdapter/tests ON, benchmarks OFF, and `BinanceMarketDataContracts_DIR`
pointing to the same selected Gateway message package. No Projection source,
Recorder, Gateway tracked file or production service was changed.

## Independent review and delivery

A fresh subagent reviewed C0 and C1 against actual Gateway/Projection code,
Conan graph, installed provenance and exported RREV; **no actionable findings**.
Its independent C0 tests: 127 passed; full suite without injected CMake inputs:
666 passed / 9 expected skips. The complete primary run above supplies those
inputs and passes all 675. This is a distinct review, not self-review.

Independent final review of clean `abc1d97b3fc87346e6316148d8b31008d8a2f774`
re-read the completed evidence and all test/export logs, with no actionable
findings. C1 technical closure is complete. [PR #23](https://github.com/tomohikoAmada/BinanceMarketDataContracts/pull/23)
is the delivery/CI/merge record; this document does not substitute historical
baseline CI for the PR candidate checks. The existing workflow automatically
runs its larger C++ matrix. Initial final-head CI
[39100977623](https://github.com/tomohikoAmada/BinanceMarketDataContracts/actions/runs/39100977623)
passed Python 3.11/3.12/3.13, Buf and graph boundaries, but the gRPC lock
regeneration step failed: without selecting `grpc/conan.lock`, it resolved newer
OpenSSL 3.6.5 instead of the committed 3.6.4. That failure is retained.
The bounded fix supplies each existing lock explicitly to `conan lock create`
and keeps the existing comparison and replay checks. Local resolution and
identity comparisons pass for both graphs; the independent subagent also
reviewed this fix and rechecked both generated locks with the original comparator,
with no actionable findings. No lock, package pin, matrix or
C++ export input changes; subsequent candidate CI is recorded on the PR.

