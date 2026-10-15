# TIDAL 0.1.0 release verification

Verified on 2026-10-15 against the published [TIDAL 0.1.0 release](https://github.com/Kalinka-Player/kalinka-plugin-tidal/releases/tag/kalinka-plugin-tidal-v0.1.0).

| Field | Verified value |
| --- | --- |
| Source tag | `kalinka-plugin-tidal-v0.1.0` |
| Source commit | `aa017f9d26c561a2b5218d99145979624d5237df` |
| Published at | `2026-10-15T21:06:47Z` |
| Artifact | `kalinka-plugin-tidal_0.1.0_all.deb` |
| Size | 27,568 bytes |
| SHA-256 | `44eedca870fc45d6aaaed6876c44bef8e1839d7efa5d4a6ca63900e106a0ef22` |
| DEB Package / Version / Architecture | `kalinka-plugin-tidal` / `0.1.0` / `all` |
| Python distribution / version | `kalinka-plugin-tidal` / `0.1.0` |
| Entry point | `kalinka_plugin_tidal = kalinka_plugin_tidal:KalinkaPluginTidal` |

Downloaded all three published assets: the DEB, `SHA256SUMS`, and `build-info.json`. Their byte lengths and SHA-256 hashes match the GitHub asset records. The DEB also matches the checksum file, build metadata and canonical Debian 13 ARM64 CI artifact byte for byte.

Inspected native headers, the embedded wheel and control scripts without installing the package or executing its maintainer scripts. The only payload file is the `py3-none-any` wheel under `/opt/kalinka/wheels/`. Wheel metadata requires Python `>=3.11`, `kalinka-plugin-sdk>=3.11,<4`, and `tidalapi>=0.8.11,<0.9`; its version, entry point and declared dependencies agree with the tagged source. The plugin inherits the SDK's `input_module` type and declares ID `tidal`.

DEB dependencies are `kalinka-plugin-sdk (>= 3.11)`, `kalinka-plugin-sdk (<< 4)`, `python3 (>= 3.11)`, and `ca-certificates`. The package has no `postinst`; its trigger activates `kalinka-server-restart`, and its `prerm` removes the installed Python distribution on removal or deconfiguration. These files match the tagged source.

The [release workflow](https://github.com/Kalinka-Player/kalinka-plugin-tidal/actions/runs/38807007707) passed Python 3.11/3.13 tests and four native runner/container builds:

| OS | Architectures | Validation |
| --- | --- | --- |
| Debian 13 | ARM64, amd64 | Build DEB, inspect package, install embedded wheel, run 49 tests |
| Ubuntu 24.04 | ARM64, amd64 | Build DEB, inspect package, install embedded wheel, run 49 tests |

Tests use the SDK shipped by released Kalinka Player 5.9.1. The published architecture-independent package comes from Debian 13 ARM64, using Python 3.13.5. The catalog restricts the release to the four tested targets even though the DEB architecture is `all`.

This evidence covers packaging and automated behavior with fake TIDAL API responses. Live account sign-in, real catalog availability and playback have not been verified with a TIDAL account. Playback supports direct unencrypted FLAC/MP3 only; DASH, encrypted streams and AAC/MP4 are unsupported. TIDAL collections are read-only. The catalog records an unofficial, experimental plugin and manual data rollback; this does not certify native installation recovery or automatic updates.
