# ARM64 fallback image construction

## Environment

Remote native ARM64 c7g.4xlarge:16 CPUs,32 GiB RAM,500 GB disk; Docker29.6.0 and Buildx0.34.1. BuildKit parallel stages2 and compile jobs4. CUDA13.0.3,Python3.12 and Rust1.92.0. Base image indexes and ARM64 manifests are in base-images.json inside the archive.

## Setup

Verify SHA256SUMS, extract evidence.tar.gz, and verify every member against files.json. Obtain the authorized source commit below into a clean build context. Materialize its docker/Dockerfile as Dockerfile.fallback, then apply recipe.patch with patch -p0. Copy the archived context/fallback-build directory into that context. The resulting Dockerfile SHA256 must be b91989202c97ea5c752e246a8c98b1f5ceab4e69a4778123cfdd5a1a270d6d51.

Use a native ARM64 Docker build host. Create the dedicated docker-container builder with the archived buildkitd.toml, and run build-command.json with paths changed to the new context and output directory. The command pins local source mode, all build targets, CUDA13.0.3,Python3.12,sglang-kernel0.4.11,FlashInfer0.7.4 and Mooncake0.3.13.post1. constraints.txt pins kernels0.14.1. The recipe installs the hash-pinned SM103a wheel and verifies runtime source and Rust import.

## Commit

Runtime52ef77912fd004f34cfe340b392018632ce69c2c. All12586 tracked files and nine symlink targets matched the clean Git source before build. Source archive SHA25637cb86844fa83229f2abc645e01e17b3a1b0d44983ab0f3a91ef71d7202be93e. Runtime source is obtained from its Git revision; the archive contains construction inputs and receipts.

## Scripts

build.py and launch.py are the recorded bounded build driver and launcher. build-command.json contains the exact invocation; plan.json preserves the original preparation state. result.json is the terminal result. recipe.patch reconstructs the image recipe from the pinned upstream Dockerfile; verify_image.py checks the installed source and dependencies.

## Workload

One CPU image build, followed by an independent network-disabled container executing /opt/glm5lp/verify_image.py. GPU serving and accuracy workloads remain pending. The build started20:14:11UTC and completed21:21:05UTC on November16.

## Results

Construction completed with build and builder-stop exit0. The loaded linux/arm64 image occupies16432566868 bytes. Its local OCI manifest is sha256:5f7484840d748eede4c87cf85de632bc35e1eba48ccda63d308f37b9db98a02a; its config digest is sha256:f6ed602706a063c2c1af76cd499d567cb66ebcd2b1b3ad9f31025f0e9cd1332f. Docker29 reports the manifest as the image ID. Private registry publication and its immutable registry reference remain pending.

Both build-time and independent loaded-image checks verify5517 tracked Python/Rust runtime files,11 exact package versions and the bundled Rust extension with build mode never. Rust extension SHA256ba2a6eff23503b7bdd6d0e7a196beb79af9019d563e35287ee55e939b9c60c48. loaded-image-verification.json records all versions and eight JIT providers, including SM103a. Matching CPU receipts establish construction checks; GPU serving, correctness and performance qualification remain pending.

## Data and Figures

The compressed archive preserves raw build logs, commands, metadata, process handles, source manifest and both verification receipts. files.json hashes every archive member. image-inspect.json retains loaded-image metadata. This candidate becomes eligible for the fallback handoff only after registry publication and required image-level GPU qualification.
