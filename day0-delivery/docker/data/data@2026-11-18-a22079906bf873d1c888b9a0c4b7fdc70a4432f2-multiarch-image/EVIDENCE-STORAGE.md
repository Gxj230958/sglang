# Local Evidence Storage

Large source and build artifacts remain on the coordinator host outside Git. They are not release artifacts and must not be confused with the published image digests in `repro.md`.

| Local path | Bytes | SHA256 | Git disposition |
|---|---:|---|---|
| `/tmp/glm-cutoff-doc/image/sglang-src.tar.gz` | 45,993,021 | `e39d419e5669a165ea019ecb57ecc07867cd5128318260686bebb2a175fd8c13` | Excluded; regenerate with `make-manifest.sh` from the pinned source |
| `/tmp/glm-cutoff-doc/glm-loop-1118-image-build.tar.gz` | 635,455 | `ad9e0c06d293e8203c821bb017c64bf9da70f3bd177f54f63d9e43c05fb25725` | Excluded; original build-kit archive |
| `/tmp/glm-cutoff-doc/patch/sglang-glm-loop-1118.patch` | 1,160,367 | `ed6a00c019cd3e58ef1518b33dff18452f12da9bb5fc42db80f55bb69a2968db` | Excluded; use the pinned source commit instead |
| `/tmp/glm-cutoff-doc/image/logs/build-amd64.log` | 415,780 | `5007841a0fd277019556383b055579bb42443aca316c43a688ec1fc81ad95a42` | Excluded; raw build log retained locally |
| `/tmp/glm-cutoff-doc/image/logs/build-arm64.log` | 416,163 | `c59fabfe4ff1b3eb4f9a778694a886ac873db936224bb4f537e2387063e0d280` | Excluded; raw build log retained locally |

The original Chinese build guide and document-export responses are also local-only. The included `repro.md` is the English reproduction record; no credentials or registry access tokens are included in this round.
