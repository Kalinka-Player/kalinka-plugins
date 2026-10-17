# TIDAL release verification

## 0.2.1

Verified on 2026-10-17 against the published [TIDAL 0.2.1 release](https://github.com/Kalinka-Player/kalinka-plugin-tidal/releases/tag/kalinka-plugin-tidal-v0.2.1).

| Field | Verified value |
| --- | --- |
| Source tag | `kalinka-plugin-tidal-v0.2.1` |
| Source commit | `9ed68844a22935f9bd799269516dab12afa33148` |
| Published at | `2026-10-17T18:39:12Z` |
| Artifact | `kalinka-plugin-tidal_0.2.1_all.deb` |
| Size | 32,216 bytes |
| SHA-256 | `a1df8c39def5b216262b4545f68720772534ea4a6bb9dae278e12e884ffa94a5` |
| DEB Package / Version / Architecture | `kalinka-plugin-tidal` / `0.2.1` / `all` |
| Python distribution / version | `kalinka-plugin-tidal` / `0.2.1` |
| Entry point | `kalinka_plugin_tidal = kalinka_plugin_tidal:KalinkaPluginTidal` |

Downloaded the DEB, `SHA256SUMS`, and `build-info.json`. All three match their GitHub asset sizes and SHA-256 digests and the canonical Debian 13 ARM64 CI artifacts byte for byte. The DEB also matches its checksum file and build metadata, including the tagged source commit.

Inspected native headers, the embedded wheel, dependencies, entry point, trigger and removal script without installing the package or executing its contents. The only payload file is the `py3-none-any` wheel under `/opt/kalinka/wheels/`; its Python modules match the tagged source byte for byte. Dependencies, the trigger and the removal script are unchanged from 0.2.0, as are the repository's packaging files.

The [release workflow](https://github.com/Kalinka-Player/kalinka-plugin-tidal/actions/runs/39058929119) passed all 129 tests on Python 3.11 and 3.13, plus package builds, inspections and packaged-wheel tests on Debian 13 and Ubuntu 24.04, each on ARM64 and amd64. The published package comes from Debian 13 ARM64 with Python 3.13.5.

This release warns in plugin settings when TIDAL ends the session and offers a new sign-in link, checking the session every 10 minutes. An outage of TIDAL's sign-in server, or a track TIDAL refuses to play, no longer interrupts the sign-in. Albums and playlists whose track count includes tracks TIDAL no longer lists are added instead of failing; listed tracks that cannot be streamed are queued and fail when played. Earlier release records and artifact digests are retained unchanged.

These changes are covered by automated tests with fake TIDAL responses; they have not been verified live with a TIDAL account. The stable classification, unofficial tier and manual data rollback policy are unchanged.

## 0.2.0

Verified on 2026-10-17 against the published [TIDAL 0.2.0 release](https://github.com/Kalinka-Player/kalinka-plugin-tidal/releases/tag/kalinka-plugin-tidal-v0.2.0).

| Field | Verified value |
| --- | --- |
| Source tag | `kalinka-plugin-tidal-v0.2.0` |
| Source commit | `c98ee1a9015b6308cfb2b5377ef46935ca20a896` |
| Published at | `2026-10-17T12:37:15Z` |
| Artifact | `kalinka-plugin-tidal_0.2.0_all.deb` |
| Size | 31,260 bytes |
| SHA-256 | `6b619a6dafa7a9d13a20a287508f77a13b04c0a9694f1088c34befde95350c33` |
| DEB Package / Version / Architecture | `kalinka-plugin-tidal` / `0.2.0` / `all` |
| Python distribution / version | `kalinka-plugin-tidal` / `0.2.0` |
| Entry point | `kalinka_plugin_tidal = kalinka_plugin_tidal:KalinkaPluginTidal` |

Downloaded the DEB, `SHA256SUMS`, and `build-info.json`. All three match their GitHub asset sizes and SHA-256 digests and the canonical Debian 13 ARM64 CI artifacts byte for byte. The DEB also matches its checksum file and build metadata, including the tagged source commit.

Inspected native headers, the embedded wheel, dependencies, entry point, trigger and removal script without installing the package or executing its contents. The only payload file is the `py3-none-any` wheel under `/opt/kalinka/wheels/`. The DEB now depends on `kalinka-server (>= 5.11.0), kalinka-server (<< 6)`; Python and SDK requirements, the trigger and the removal script are unchanged from 0.1.1 and match the tagged source.

The [release workflow](https://github.com/Kalinka-Player/kalinka-plugin-tidal/actions/runs/39033151558) passed all 112 tests on Python 3.11 and 3.13, plus package builds, inspections and packaged-wheel tests on Debian 13 and Ubuntu 24.04, each on ARM64 and amd64. All use the SDK from released Kalinka Player 5.9.1. The published package comes from Debian 13 ARM64 with Python 3.13.5.

This release signs in by device authorisation, adds the Lossless and Max quality choice, plays TIDAL's DASH streams and AAC or MP4 streams through renderer 0.10.0, and lists Home, Explore, Genres and Moods at the root again. Earlier release records and artifact digests are retained unchanged.

Sign-in and playback were verified live with a TIDAL account on 2026-10-17. Automated tests use fake TIDAL responses, including real manifests run through tidalapi's parser. Encrypted streams and Dolby Atmos are refused. Collections remain read-only. The plugin is now classified stable; the unofficial tier and manual data rollback policy are unchanged.

## 0.1.1

Verified on 2026-10-16 against the published [TIDAL 0.1.1 release](https://github.com/Kalinka-Player/kalinka-plugin-tidal/releases/tag/kalinka-plugin-tidal-v0.1.1).

| Field | Verified value |
| --- | --- |
| Source tag | `kalinka-plugin-tidal-v0.1.1` |
| Source commit | `dfb6c8a25d0e900963b0b590f20d24332dc8193f` |
| Published at | `2026-10-16T18:48:02Z` |
| Artifact | `kalinka-plugin-tidal_0.1.1_all.deb` |
| Size | 30,228 bytes |
| SHA-256 | `f9474fe42b087246497a86855ea3311b6a6943c8bd67e3719d8814a6ecb9bc1b` |
| DEB Package / Version / Architecture | `kalinka-plugin-tidal` / `0.1.1` / `all` |
| Python distribution / version | `kalinka-plugin-tidal` / `0.1.1` |
| Entry point | `kalinka_plugin_tidal = kalinka_plugin_tidal:KalinkaPluginTidal` |

Downloaded the DEB, `SHA256SUMS`, and `build-info.json`. All three match their GitHub asset sizes and SHA-256 digests and the canonical Debian 13 ARM64 CI artifacts byte for byte. The DEB also matches its checksum file and build metadata, including the tagged source commit.

Inspected native headers, the embedded wheel, dependencies, entry point, trigger and removal script without installing the package or executing its contents. The only payload file is the `py3-none-any` wheel under `/opt/kalinka/wheels/`. Python and SDK requirements, native dependencies and maintainer scripts are unchanged from 0.1.0 and match the tagged source.

The [release workflow](https://github.com/Kalinka-Player/kalinka-plugin-tidal/actions/runs/38949896126) passed all 75 tests on Python 3.11 and 3.13, plus package builds, inspections and packaged-wheel tests on Debian 13 and Ubuntu 24.04, each on ARM64 and amd64. All use the SDK from released Kalinka Player 5.9.1. The published package comes from Debian 13 ARM64 with Python 3.13.5.

This release adds an account reset setting and visible sign-in and quality information, reduces the catalog root to My Collection and My Mixes, fixes complete queue additions, and preserves stable catalog section links. Saved discovery links remain resolvable. Earlier release records and artifact digests are retained unchanged.

Automated tests use fake TIDAL responses, including account replacement and session restoration. Live account sign-in and playback remain unverified. The plugin automatically requests CD-quality lossless audio; TIDAL Max / hi-res, DASH, encrypted and AAC/MP4 playback remain unsupported. Collections remain read-only. The unofficial, experimental classification and manual data rollback policy are unchanged.

## 0.1.0

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
