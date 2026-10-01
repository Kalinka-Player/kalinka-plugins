# Plugin hub architecture and scope

Decision: use a curated GitHub catalog and native packages for managed Linux servers. Authors publish packages in their own source repositories; the hub records exact releases, compatibility and provenance. GitHub is the initial review/source host, not the security boundary or a runtime dependency on the GitHub API.

This initial implementation registers seven plugins, including Spotify and Qobuz as unofficial, validates/builds metadata, and supplies a tested reference OS/architecture filter. Server installation, automatic updates, signed hosting and Flutter integration are deliberately outside the initial commit. Runtime behavior below is the design, not functionality shipped by this repository.

## Why native packages

DEB/RPM align with Kalinka's existing deployment. Spotify needs both its Python module and a patched librespot executable; native packages deliver both, express OS dependencies and participate in package ownership and service lifecycle. Keep wheels inside those packages as an implementation detail; no SDK or plugin-discovery rewrite is necessary.

Wheels can contain native extensions too: their [platform/ABI tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) are designed for that. The decision is about system integration, not Python being unable to ship native code. A wheel adapter may eventually suit development or non-native-managed deployments, but must not overwrite a DEB/RPM-owned plugin.

Costs are a distro/architecture build matrix and elevated trust. Package scripts execute during lifecycle operations, and failure can leave a partially configured installation; native packaging is not automatic application-health rollback. See [Debian's maintainer-script lifecycle](https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html) and [RPM dependency semantics](https://rpm.org/docs/latest/manual/dependencies.html).

Kalinka's current native packages still feed wheels into a shared Python environment during service bootstrap. Native packaging does not resolve all Python dependency conflicts. Before unattended updates, dependency preparation and failed-bootstrap recovery need explicit design and tests. Existing Debian triggers and RPM scriptlets can restart the server themselves; coordinated restart timing needs a packaging/worker protocol, not just a UI promise.

## Classification and discovery

The required `type` uses the existing SDK values: `input_module` appears as Input sources; `output_device` appears as Device control. Authors declare the value inherited from their SDK plugin class and curators verify it. The server's normal detection remains authoritative after installation. A mismatch should be reported for correction without changing how the installed plugin is loaded or where its configuration belongs. An import failure is unknown detection, not another type. Detection alone does not register a manually installed plugin for updates.

Keep `tier` (official/unofficial), `maturity` (stable/experimental/deprecated), `type`, and `delivery` (bundle/independent) independent. Output devices declare model/family names and readable requirements in `device_support`; index these names for search and render their limitations. The basic lists are not a verified per-release hardware compatibility matrix.

## Compatibility contract

Evaluate the **server host**, not the phone/tablet running KalinkaAI. Native package architecture and the runtime's userspace must agree; CPU capability or `uname -m` alone is insufficient on a 32-bit userspace. Native-managed installations derive architecture from their package manager and verify the running environment. Container/development installs need an explicitly supported deployment adapter; do not manage host packages from a container by assumption.

| Field | Meaning |
| --- | --- |
| `requires.platforms` | Release-level OS allowlist; `all` alone means no OS restriction. |
| `requires.architectures` | Release-level userspace architectures; `all` alone means architecture-independent. |
| Artifact `platform`, `architectures` | Additional constraints for these exact bytes. |
| Artifact `format` | `deb`, `rpm`, or portable/development `wheel`; must match the deployment adapter. |
| Native `package` | Exact name, backend-native version, and native architecture from package headers. |
| Native `targets` | Exact distro `ID` / `VERSION_ID` allowlist, independently of CPU architecture. |
| `requires.server/sdk/python/renderer` | PEP 440 ranges for component versions; renderer optional, but mandatory to check when declared. |
| `requires.capabilities` | Recognized, machine-checkable runtime capabilities. Unknown or unobservable requirements fail closed. |

Server and renderer compatibility is expressed using released version ranges, never source commit IDs or repository ancestry. Users install prebuilt components. Plugin `source_commit` and catalog `revision` remain build/audit provenance only; they are not installed-component requirements and must not appear as such in the UI.

Canonical architecture aliases include DEB `amd64` → `x86_64`, DEB `arm64` → `aarch64`, and DEB `all` / RPM `noarch` → `all`. A DEB with `all` architecture is still Linux-only and distro-limited. The initial Spotify records admit x86-64 and ARM64 only; Qobuz's DEB is architecture-independent. All still require an eligible server, package backend and resolvable dependencies.

`artifact_supports_target` in the builder is a reference filter for validated data. It rejects unknown host identities, wrong package format, mismatched architectures and unlisted distro versions. It is only one input to an install decision, not authorization. The eventual server must additionally:

1. Verify signed catalog trust/freshness, identity ownership and non-withdrawal; retain last-known-good metadata for offline browsing.
2. Check all component ranges, capabilities and release/artifact target intersections. Unknown renderer version blocks a release requiring that renderer; the user sees the reason. Do not upgrade server/SDK/renderer silently to satisfy a plugin.
3. Select the highest compatible release, not simply the newest release. Match an exact native artifact; reject ambiguous candidates. Wheel deployments additionally check Python ABI and platform tags, including libc/deployment baselines.
4. Download the exact URL with size limits and a redirect policy that blocks local/private network destinations; verify byte length, SHA-256, native headers and contained distribution identity before privileged execution. No catalog shell commands, live git clone/build, or `curl | sh`.
5. Simulate the apt/dnf transaction and prepare Python dependencies. Refuse unintended removals, core changes, repository changes, incompatible dependencies, or ownership collisions. Display the approved transaction and revalidate it at execution time.

Initial distro allowlists deliberately cover Debian 13, Ubuntu 24.04, and Fedora 44 (Spotify only). These are curated constraints derived from upstream support statements, not claims of completed hardware testing. Derivatives must expose an explicitly listed OS identity; `ID_LIKE` or a newer version never grants support automatically. Bundled entries with no releases inherit server-package support and cannot be independently installed through the hub.

## API and installation lifecycle

KalinkaAI talks to the server, which fetches/caches the public catalog anonymously for browsing. Signature-verified metadata and independent installed-payload evidence are separate prerequisites for managed identity and updates. Target endpoints are listed below; the implemented read-only subset and unavailable capabilities are described under manual-install recognition.

| Endpoint | Result |
| --- | --- |
| `GET /server/plugins` | Installed inventory, origin, catalog binding, verification status/reason and update eligibility. |
| `GET /server/plugins/catalog` | Catalog entries, installed versions, compatible candidates and blocking reasons. |
| `GET /server/plugins/updates` | Compatible updates for verified catalog installations; stale/checking/error status. |
| `POST /server/plugins/plans` | Resolve plugin/version to a short-lived plan bound to catalog revision, artifact digest, host state and dependency transaction. |
| `POST /server/plugins/operations` | Accept a confirmed plan plus idempotency key; return `202` with durable operation ID. This is the install/update call. |
| `GET /server/plugins/operations/{id}` | Download, verification, installation, restarting, health-check, completion or recovery-required status. |

Mutation requires authenticated administrative authorization and appropriate CSRF/origin protection. The client sends a plugin identity or plan, never a privileged command or arbitrary installer URL. A small privileged broker with a restricted interface runs package-manager operations; the REST process must not gain unrestricted root access.

Persist state before side effects. A systemd-supervised worker must survive the Kalinka server restart, serialize package transactions, honor package-manager locks, and reconcile interrupted operations on boot. Confirm playback interruption before enqueueing an operation that may trigger a restart. Only report success after the expected distribution/version loads and server health checks pass; reconnecting the HTTP API alone is insufficient.

Native transaction success does not prove plugin health. Retain previous artifacts and configuration backups, but only attempt downgrade when both data compatibility and backend recovery are tested. Otherwise stop with an actionable recovery-required state. Do not promise atomic venv-swap rollback for native packages that have changed system files or executed scripts. The initial independent releases declare `data_rollback: manual`, so unattended updates remain disabled.

Record catalog identity, plugin ID, installed distribution, source, package ownership, version and artifact digest. Installation origin is independent of catalog identity: a manually installed genuine catalog release is recognised automatically after verification, without a forced reinstall. A name-only match never grants a binding or update permission. Unverified replacements require explicit consent. Bundle-owned plugins stay with the server bundle; Kalinka's RPM currently bundles its core plugins, while Debian supplies separate packages. Do not shadow those with another owner.

## Recognition of manually installed releases

Discover distributions and entry points without importing code, using names/versions only to look up candidate releases. Authenticate the expected release through the signed catalog, binding plugin identity, package identity, platform and artifact SHA-256 to Kalinka's provisioned trust root. A hash or key declared by the installed plugin is not proof. Keep historical catalog releases so older manual installations can be recognised; unknown or editable builds remain unmanaged.

The archive digest is not the installed-directory digest. Recognition also requires an authenticated installed-payload manifest derived from verified release bytes and approved installation transformations. It specifies distribution/version/entry point, the artifact digest and a complete list of expected paths, sizes and SHA-256 values within exclusively owned directories. Its digest/length must be pinned by the authenticated catalog. This is a new publication contract, not data currently present in the seven seed entries.

Verify native files, the staged wheel and the active Python installation, including entry-point metadata. Reject unexpected files, ambiguous owners, import shadowing and duplicate distributions/entry points. A pristine staged wheel cannot authenticate altered active code. Never use installed `RECORD` hashes as the expected truth. Configuration/user data live outside immutable scopes; generated wrappers, installer metadata and bytecode need explicit trusted handling. Unknown generated files or symlinks remain unverified rather than being broadly ignored. Root paths come from trusted deployment configuration, never arbitrary catalog paths or executable probe commands.

An independent worker verifies without executing plugin code, checks package ownership and the actual runtime resolution, and stores a protected receipt tied to the installed generation, catalog/release, archive/manifest digests, method and time. The receipt does not replace revalidation before an update or after external changes. Distinguish archive provenance from installed-payload equivalence; do not invent the hash of the package originally installed. Inspection must not execute package-provided verification scripts.

Successful verification automatically binds a manual installation to its catalog release. Preserve `origin: manual` separately from `catalog_match: verified`. It follows the same configured update policy as an app-installed release, without another adoption prompt. A verified match is eligibility for update checks, not automatic enrollment in unattended installation or a waiver of compatibility/recovery checks. An outside upgrade to another genuine release can verify again. Unknown, modified, ambiguous or unregistered installs remain usable and receive no unattended updates; offer explicit verified replacement where appropriate.

The REST inventory exposes origin, catalog match, verification status/reason and binding separately. Update responses distinguish identity eligibility, candidate compatibility, dependency planning and automatic-install permission. The current server backend (REST API 0.9) supplies import-free discovery, payload-verification/reconciliation primitives, read-only inventory routes and anonymous public catalog browsing. `GET /server/plugins/catalog` returns the cached validated feed with unverified trust, unevaluated host compatibility and installation disabled; it returns `503 catalog_unavailable` only when no browsing document is available or fetching is disabled. Its production service still has no signature-verifying catalog adapter or independent worker adapter: update checks explicitly report unavailable, and no mutation routes or automatic updates are enabled. Verification succeeds only in controlled unit fixtures until those adapters are connected; raw GitHub JSON and self-reported `verified` flags are never accepted as proof.

Threat boundary: the host, verifier, package database, runtime and dependencies must be trusted. This does not sandbox plugins, detect all malicious behavior, prove past root-level installation scripts were safe, or survive administrator compromise. Test copied identities, forged metadata, changed/extra files, symlink/path attacks, stale evidence, external upgrades and duplicate ownership before enabling managed updates.

## Publication and updates

Keep one reviewed source JSON per plugin and build a deterministic versioned catalog. A GitHub PR workflow provides a good initial curation/audit process; a database/API registry is unnecessary at this size. Published static metadata can later move to independent object storage/CDN without changing plugin identities. The app should never depend on GitHub search, API credentials or rate limits to resolve installations.

The generated root `catalog.json` is the unsigned browsing feed; CI checks it against `plugins/` without downloading any packages. Once committed and pushed, GitHub serves it publicly at `https://raw.githubusercontent.com/Kalinka-Player/kalinka-plugins/main/catalog.json`. No account, API token or access authentication is required. Public access does not waive publisher signature verification for installation, or administrator authorization for the REST install operation.

The server's `KALINKA_PLUGIN_CATALOG_BASE_URL` defaults to `https://raw.githubusercontent.com/Kalinka-Player/kalinka-plugins/main/`. It appends `catalog.json`; an explicitly empty setting disables fetching. Move to `https://kalinkaplayer.com/plugins/` after publishing the same feed there, keeping `catalog_id: "kalinka"`, plugin IDs and, once provisioned, signing trust unchanged. Hostnames are delivery locations, not installed-plugin identities. A copied unsigned catalog ID is not proof of publisher identity. The setting is deployment-only, not writable by REST clients. Configure the final HTTPS origin directly: the reader does not follow redirects or use ambient proxy/credential settings.

For initial browsing tests, the server checks the bundled v1 schema and basic identity/release consistency, enforces a 2 MiB download bound and timeouts, and retains last-valid in-memory data on failure. It refreshes at startup and hourly with jitter, conditional requests and failure backoff; reads never fetch. API responses distinguish available, stale, unavailable and disabled data, and explicitly report signature trust as unverified and compatibility as not evaluated. The cache currently lasts for one server process only. No package or plugin-link downloads occur during browsing. Neither a schema check nor its diagnostic content hash authorizes installation or binds an installed plugin.

Before production catalog-driven installation, add signed metadata (for example TUF), a bundled trust root, key rotation, expiry/rollback protection and protected review/signing. Signing does not require making the catalog private. TLS, a Git commit and hashes fetched beside mutable artifacts are not substitutes for catalog authenticity. Changes to existing asset bytes/digests require a new release, not silent replacement. Keep previous compatible releases; withdrawals block new selection without authorizing removal from users' machines.

Server-side update checks run on a schedule with jitter and conditional requests, cache results, and re-evaluate installed inventory after changes. Offline/stale metadata must be visible. Automatic installation is a separate, explicit opt-in policy for registered plugins, constrained by compatibility, trust, restart windows and recoverability. Listing an available update is not permission to interrupt playback.

## Chosen app interaction

The entry point is the existing server menu → Plugins. The chosen design uses expandable entries in one Plugins destination, with local Browse, Installed and Updates views and Input sources/Device control filters. Details, model lookup and operation progress stay inline. One transient dialog confirms restart timing. The separate detail-page alternative is superseded; complex device configuration uses peer Server settings rather than a third-level catalog screen.

The app reads server-evaluated results, not each author's repository independently. Device entries separately explain whether the server can run the plugin, what controls it implements, and whether a particular model has evidence of support. An unknown model or disconnected device must not be labelled verified. Rich version/firmware/zone-specific records remain a future schema extension.
