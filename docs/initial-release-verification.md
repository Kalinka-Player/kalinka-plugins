# Initial release verification

Checked on 2026-10-01. This records catalog curation evidence, not an end-to-end installation certification. No package was installed and no maintainer script or plugin code was executed. CI remains offline; these checks are not an automated publication pipeline.

## Published bytes and identity

Downloaded all four packages and `SHA256SUMS` from [Spotify 0.2.0](https://github.com/Kalinka-Player/kalinka-plugin-spotify/releases/tag/kalinka-plugin-spotify-v0.2.0), and the package/checksum file from [Qobuz 5.0.1](https://github.com/Kalinka-Player/kalinka-plugin-qobuz/releases/tag/kalinka-plugin-qobuz-v5.0.1). Checked SHA-256 against both the release checksum file and GitHub's asset digest, and recorded byte lengths in the manifests.

Read package headers with `dpkg-deb -f` and `rpm -qp`; these query archive metadata without installation. Spotify DEBs declare `amd64`/`arm64`, version `0.2.0`; RPMs declare `x86_64`/`aarch64`, epoch `0`, version/release `0.2.0-1.fc44`. Qobuz declares `all`, version `5.0.1`. Names match their catalog distributions. Source tags resolve to the full commits recorded in each manifest.

An upstream checksum agreement is not independent publisher authentication. Production publication must also inspect payload/embedded wheel identities and scripts, preserve immutable historical digests, and sign the catalog. A runtime installer must independently verify the downloaded bytes again.

## Requirements evidence

- [Spotify's source](https://github.com/Kalinka-Player/kalinka-plugin-spotify/tree/348cd564cb0a4f82dce00f492691eee23033a0b4) declares Python ≥3.11 and SDK ≥3.5,<4; native package headers confirm SDK/Python dependencies. Source documentation identifies patched librespot and Spotify Premium requirements.
- Spotify's companion-core requirement is [KalinkaPlayer commit ad91659](https://github.com/Kalinka-Player/KalinkaPlayer/commit/ad91659ba259f9dbc195f3618653985116407263). Local repository tag ancestry places it in server `kalinka-v5.3.0` and renderer `kalinka-renderer-v0.5.0`; upgrading only the SDK is insufficient. The catalog conservatively caps server/renderer at the next major version until reviewed.
- [Qobuz's source](https://github.com/Kalinka-Player/kalinka-plugin-qobuz/tree/c8fe6ec795c784598f4e9dafd4ee47ca47d060a2) declares Python ≥3.10 and SDK ≥3.4,<4. Its README requires server ≥5.2 for plugin v5 and an active subscription. The catalog conservatively caps the server at the next major version.
- Spotify's documented distro support includes Debian 13, Ubuntu 24.04 and Fedora 44. Qobuz describes compatible Debian/Ubuntu servers more broadly. The hub starts with those explicit distro versions only (no Qobuz RPM). These allowlists are stricter than some upstream claims, not evidence of additional testing. Expand through review as targets are confirmed.

Both independent plugins are unofficial and experimental. Stable-channel release records mean final version numbers, not a change in plugin maturity. Data rollback has not been certified, so both records require manual recovery policy.
