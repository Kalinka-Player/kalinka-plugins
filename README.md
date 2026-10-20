# Kalinka Player Plugin Hub

The curated plugin catalog for [Kalinka Player](https://github.com/Kalinka-Player/KalinkaPlayer). Discover input sources and optional amplifier or AVR controls, with creator, source, license, plugin type, and hardware-support metadata.

This initial hub contains ten registered plugins, a JSON schema, an offline validator/catalog builder, and validation CI. It does **not** install plugins or enable automatic updates. The five bundled plugins update with Kalinka Player; Spotify, Qobuz, TIDAL, Roon Bridge and AirPlay have independent source repositories and native release records with exact download URLs and checksums.

## Official

| Plugin | Type | Description |
| --- | --- | --- |
| [My Library](plugins/localfiles.json) | Input source | Play your own music files from the server or a network share. |
| [Jamendo](plugins/jamendo.json) | Input source | Free music from Jamendo, published under Creative Commons. |
| [UPnP](plugins/upnp.json) | Input source | Play to Kalinka Player from UPnP apps on your network. |

My Library, Jamendo and UPnP are the only official plugins in this catalog. All three are included in the Kalinka Player server bundle, not independently updatable through this catalog.

## Unofficial

| Plugin | Type | Description |
| --- | --- | --- |
| [MusicCast](plugins/musiccast.json) | Device control | Control the volume and power of a Yamaha MusicCast device. |
| [Dummy Device](plugins/dummydevice.json) | Device control | A pretend output device for testing plugins. |

These two plugins are bundled with Kalinka Player and update with the server; being bundled does not make a plugin official. MusicCast declares its MusicCast / Yamaha Extended Control family and readable limitations; a verified exact-model list is not yet available.

| Plugin | Type | Source and existing releases | Requirements |
| --- | --- | --- | --- |
| [Spotify Connect](plugins/spotify.json) | Input source | [Source](https://github.com/Kalinka-Player/kalinka-plugin-spotify) · [Releases](https://github.com/Kalinka-Player/kalinka-plugin-spotify/releases) | Linux, Python 3.11+, server ≥5.3.0 and <6.0.0, renderer ≥0.5.0 and <1.0.0, SDK ≥3.5 and <4, Spotify Premium, and patched librespot. |
| [Qobuz](plugins/qobuz.json) | Input source | [Source](https://github.com/Kalinka-Player/kalinka-plugin-qobuz) · [Releases](https://github.com/Kalinka-Player/kalinka-plugin-qobuz/releases) | Active Qobuz subscription; Python 3.11+, server ≥5.12 and <6, SDK ≥3.14 and <4. |
| [TIDAL](plugins/tidal.json) | Input source | [Source](https://github.com/Kalinka-Player/kalinka-plugin-tidal) · [Releases](https://github.com/Kalinka-Player/kalinka-plugin-tidal/releases) | TIDAL account and subscription for playback; Debian 13 or Ubuntu 24.04 on ARM64 or x86-64; Python 3.11+, server ≥5.12.0 and <6, SDK ≥3.14 and <4; renderer ≥0.10.0 for AAC, MP4 and segmented streams. |
| [Roon Bridge](plugins/roon.json) | Input source | [Source](https://github.com/Kalinka-Player/kalinka-plugin-roon) · [Releases](https://github.com/Kalinka-Player/kalinka-plugin-roon/releases) | Linux x86-64, ARM64 or ARMv7hf; Python 3.11+, Node.js 18+, SDK ≥3.7 and <4 with a Kalinka Player server implementing the external playback API; Roon Server and subscription. |
| [AirPlay](plugins/airplay.json) | Input source | [Source](https://github.com/Kalinka-Player/kalinka-plugin-airplay) · [Releases](https://github.com/Kalinka-Player/kalinka-plugin-airplay/releases) | Linux x86-64 or ARM64 on Debian 13; Python 3.11+, server ≥5.9.0 and <6.0.0, SDK ≥3.11 and <4, renderer ≥0.5.0 and <1.0.0. Bundles shairport-sync 5.5.2 and nqptp 1.2.8. |

All five integrations are registered as **unofficial**. Spotify, Qobuz and TIDAL are classified **stable**; Roon Bridge and AirPlay remain **experimental**. They are independent of the music-service vendors; registration does not imply vendor endorsement or production certification.

TIDAL reuses the unofficial `tidalapi` client to expose Home, Explore, Genres, Moods, My Mixes and My Collection, plus search and album, artist and playlist browsing. Version 0.2.0 signs in by device authorisation, offers Lossless and Max quality, and plays direct and segmented FLAC, AAC and MP3 streams; encrypted streams and Dolby Atmos are refused. Version 0.2.1 warns when the TIDAL sign-in expires and adds albums and playlists that include tracks TIDAL no longer lists; 0.2.2 retries an empty page before ending such an add. Version 0.3.0 offers TIDAL as a home source and shows artist pictures and promotion banners in the sizes TIDAL serves. Its architecture-independent DEB is built and tested on all four declared OS/architecture combinations. See [release verification](docs/tidal-release-verification.md).

Roon Bridge downloads Roon Labs' proprietary audio engine when enabled; audio plays on the Kalinka Player server's local DAC and bypasses the Kalinka Player renderer. The plugin displays metadata, artwork and progress. From 0.2.0 it routes the Kalinka Player volume slider to the Roon output on a server with external-volume support (plugin SDK 3.11 or newer; released servers up to 5.8.0 ship older SDKs and show playback without Roon volume), can attach to a Roon Server's own audio endpoint on the same machine, and keeps Roon's session across pause. It does not guarantee seamless switching between audio sources.

AirPlay makes the Kalinka Player server an AirPlay 2 or classic AirPlay speaker for an iPhone, iPad or Mac, using the bundled shairport-sync and nqptp. The audio plays through the renderer selected in Kalinka Player, which may be on another machine; the server opens no audio hardware. Its binaries link Debian 13's libraries, so its packages are for Debian 13 only, one per architecture. From 0.2.0 each stream is encoded at the sender's own rate and bit depth: 16-bit 44.1 kHz for classic AirPlay and AirPlay 2 realtime streams, 24-bit 48 kHz for Apple Music Lossless over AirPlay 2. AirPlay is a trademark of Apple Inc.; the integration is not certified or endorsed by Apple.

Initial release records are Spotify **0.2.0** and Qobuz **5.0.1**. Spotify supplies Linux DEB/RPM packages for x86-64 and ARM64; Qobuz supplies an architecture-independent DEB. Downloaded bytes were checked against their release checksums and GitHub asset digests, and native package headers were inspected without installation. See [verification evidence](docs/initial-release-verification.md).

Managed Linux delivery is **native-package-first**. The initial curated distro allowlist is Debian 13 and Ubuntu 24.04 for DEBs, plus Fedora 44 for Spotify RPMs. This intentionally does not imply support for every derivative or future distro version. A Debian `all` package means architecture-independent, **not** cross-platform. Server, SDK, Python, renderer (where declared), dependencies and package ownership must still be compatible. Follow upstream documentation for manual installation; the hub does not yet provide an installer.

## Experimental

[Dummy Device](plugins/dummydevice.json) is an unofficial development/testing plugin that simulates an output device. It controls no physical amplifier. Roon Bridge and AirPlay above are also experimental, while retaining their unofficial publisher tier.

`tier` describes maintenance authority; `maturity` describes readiness. They are independent. Plugin type is separately declared as `input_module` or `output_device`, matching the SDK.

## Catalog contract

- One reviewed document per plugin in [`plugins/`](plugins), validated by [`schemas/plugin.schema.json`](schemas/plugin.schema.json).
- Required `type` is copied from the plugin's `PLUGIN_TYPE.value`. Curators verify it; browsing never imports plugin code. After installation, Kalinka Player's detected type remains authoritative.
- Output devices require `device_support.models`, `families`, and `notes`. At least one model or family must be named, with readable prerequisites and limitations. These names support future search; a family match is not exact-model verification.
- `categories` contains descriptive search tags, not an alternative type declaration. `delivery` distinguishes bundle-owned and independent packages.
- Releases require server/SDK/Python requirements, OS and architecture declarations, versioned artifact URLs, sizes and SHA-256 hashes. Native artifacts additionally declare exact package identity and distro/version targets.
- `requires.architectures` limits the release; each artifact also declares `architectures`. Both must match the **server's userspace**, not the app device or merely the CPU. `all` is allowed only by itself and never bypasses the other requirements.
- `deb` and `rpm` are Linux-only. `wheel` remains a schema option for portable/development deployments; no wheel adapter or release is enabled here. `platform: all` and `architectures: ["all"]` are separate claims.

See [contributing](CONTRIBUTING.md), [architecture and scope](docs/architecture.md), and the real [Spotify](plugins/spotify.json)/[Qobuz](plugins/qobuz.json)/[Roon Bridge](plugins/roon.json) native-release records. The [portable-wheel example](examples/example-plugin.json) and [device-support example](examples/example-device-plugin.json) are synthetic and excluded from the built catalog.

## Validate and build

Python 3.11 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/catalog.py --revision local --output dist/catalog.json
```

The builder checks metadata, identity uniqueness, version ranges, artifact identities, OS/architecture consistency, distro allowlists and URL structure. A tested reference target filter demonstrates fail-closed selection; it is not the runtime installer. The builder produces deterministic **unsigned** JSON without downloading, installing or importing plugins. CI repeats the tests and builds a catalog using the source commit as its revision.

The result contains `schema_version: 1`, `catalog_id: "kalinka"`, `revision`, and `plugins`. A revision is an audit reference, not a signature. Neither a local build nor a raw GitHub JSON file authorizes installation. The server and app support opt-in read-only browsing with metadata-only compatibility checks. Signed publication, full artifact/payload inspection, installation and recovery remain separate work. No automatic-update authorization is enabled by this feed.

## Public browsing feed

[`catalog.json`](catalog.json) is the generated public browsing feed. After it is committed and pushed, it is available at `https://raw.githubusercontent.com/Kalinka-Player/kalinka-plugins/main/catalog.json`, without a login or GitHub token. CI refuses a feed that differs from the reviewed source entries. When plugin metadata changes, regenerate the feed and include it in the same review:

```sh
.venv/bin/python tools/catalog.py --revision "$(git rev-parse HEAD)" --output catalog.json
.venv/bin/python tools/catalog.py --check --output catalog.json
```

The revision identifies the source baseline; the document's content hash distinguishes changed bytes. Neither is signature verification. The server's public reader validates this feed for display only and reports its trust as unverified; it does not use it to register installations or authorize updates.

Set `KALINKA_PLUGIN_CATALOG_BASE_URL` on the server to change its serving location. The default is the GitHub directory above, and the reader appends `catalog.json`. An empty value disables fetching. To migrate later, publish it under `https://kalinkaplayer.com/plugins/` and point the server there, keeping `catalog_id: "kalinka"` and all plugin IDs unchanged. The hostname is not part of plugin identity. See [architecture](docs/architecture.md#publication-and-updates) for cache behavior and the separate production signing requirement.

## License

The hub's code and documentation are [GPL-3.0-or-later](LICENSE), derived from the Kalinka Player catalog scaffold. Each plugin keeps its own license, recorded in its metadata; listing it does not relicense its source or artifacts.
