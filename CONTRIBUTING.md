# Contributing a plugin

Create `plugins/<id>.json` following the schema. Keep the Kalinka `PLUGIN_ID`, distribution name, and `kalinka.plugins` entry-point name distinct and accurate. Supply the original creator, current maintainers, a description, license, and source location. Do not include private contact details or credentials. The plugin's own license continues to govern its artifacts.

Catalog maintainers verify repository ownership, reserve identities, and assign `official` or `unofficial`. New community entries should propose `unofficial`; experimental quality is an independent maturity value. Changes to ownership, identity, or trust tier require maintainer review. Do not silently retarget an abandoned plugin to a new publisher.

## Declare the plugin type

Set the required `type` to the plugin class's `PLUGIN_TYPE.value`: `input_module` for an `InputModulePlugin`, or `output_device` for an `OutputDevicePlugin`. These appear as Input sources and Device control in KalinkaAI. Keep one type per catalog entry, matching the current SDK; `categories` is only for descriptive search tags such as `library`, `radio`, or `yamaha`.

Generate this value in the author's own build/test pipeline or copy it from the reviewed class and its SDK base. Maintainers verify the declaration against source and author test evidence. Catalog CI validates data only: do not install or import an unreviewed plugin to discover its type. No new SDK type declaration or user category selection is required. A type change is a reviewed contract change, not an ordinary retagging operation.

After installation, the server uses its existing detection and reports discrepancies with the curated value. Correct catalog mistakes without changing how the installed plugin is loaded or configured. Device-control capabilities and supported models require separate evidence; knowing the type does not establish hardware compatibility.

## Describe supported devices

Every `output_device` entry must include `device_support` with `models`, `families` and `notes` arrays. Include at least one supported model or family; both may be populated. Use an empty array for the unused list, not placeholder values such as `unknown` or `all`. Use manufacturer-qualified names that a user can recognize and search, for example the fictional names in [the device example](examples/example-device-plugin.json).

Notes are required: explain the protocol/connection needed, setup prerequisites and material limitations. Family-level coverage must state its scope and any unverified exact-model coverage; do not claim every product from a manufacturer. A simulated development plugin should name its simulated family and explicitly state that it controls no real hardware. Do not publish a real device plugin with no known model or family scope. Input modules do not use this field.

Curators review these claims against the plugin implementation and the author's documentation or testing. Schema validation checks the presence and shape of this data, not whether a device actually works. The current lists support reading and search; version/firmware/zone-specific verification will need the richer support-record extension in the design.

## Register a release

1. Build from a tagged source commit in the plugin repository. Prefer DEB/RPM for managed Linux servers; these can contain the Python wheel and any native executable. Record explicit server, SDK, Python, OS and userspace-architecture requirements, plus renderer requirements if needed. Do not infer support from the author's development machine.
2. Publish versioned artifacts and release notes. For GitHub, prefer immutable releases. Copy the exact asset URLs, byte lengths, and SHA-256 values from the build. Include the source tag and full commit hash.
3. Add a release record and run the validator/tests. Keep earlier compatible releases. The plugin version must agree with the packaged Python distribution. Record the native package version separately: DEB `Version`, or RPM `[epoch:]version-release`. Native ordering belongs to dpkg/RPM, not Python version comparison. Stable records cannot contain prerelease or development versions; an experimental plugin may still publish a final-version stable-channel release.
4. Declare `data_rollback: compatible` with a `rollback_versions` range only when older versions can still read the data after this release runs. This is a data compatibility claim, NOT proof that a native transaction is reversible. Automatic updates also require a tested installer recovery path and opt-in policy. Otherwise use `manual` without a range; the initial Spotify and Qobuz releases use this conservative setting.
5. Request review. Validation of JSON is only the first step: publication must also inspect artifact bytes, native headers, embedded wheel metadata and maintainer scripts without executing them, and check that existing versions retain their digests. JSON validation does not perform these inspections.

Use `requires.notes` for operational requirements such as a service account or supported device. Use `requires.capabilities` only for recognized machine-checkable requirements; it is not a place for shell commands. Native dependencies must be available on each supported target, even when the plugin's own wheel is `all`.

New bytes require a new version. To retract a release, set `withdrawn` and explain `withdrawal_reason`; preserve its historical record. A withdrawal prevents installation and automatic updates to that release, but does not authorize deletion of users' installations or data.

## Declare OS and architecture support

Every release requires `requires.platforms` and `requires.architectures`; every artifact requires `platform` and `architectures`. Canonical architecture names are `x86_64`, `aarch64`, `armv7l`, `x86`, and `riscv64`. `all` means no architecture restriction; use it alone, never mixed with specific values. A portable file can still have narrower release requirements because of its dependencies.

For native packages, supply `package.name`, `package.version`, and `package.architecture` exactly as reported by package headers. `amd64` (DEB) maps to `x86_64`, `arm64` to `aarch64`, `armhf` to `armv7l`, and `all`/RPM `noarch` to `all`. Do not generalize Debian armhf's ARMv7 baseline to a derivative's ARMv6 build: that needs a distinct supported architecture contract. The validator cross-checks declared architecture and filename; production verification must compare actual headers too.

Native artifacts always use `platform: linux` and require `targets`, for example `[{"id":"debian","versions":["13"]}]`. Entries match exact `/etc/os-release` `ID` and `VERSION_ID` values. No `ID_LIKE` fallback, wildcard or implicit future-version support. A Raspberry Pi running 32-bit userspace cannot use an ARM64 package even if its CPU is 64-bit. Unknown identity or architecture must disable installation until curated support exists.

A `py3-none-any` wheel must declare `platform: all` and `architectures: ["all"]`; platform-specific wheels must match their tags, including both architectures for macOS `universal2`. This retained portable format is not a fallback for native-package-managed servers. Adding a wheel asset does not enable a wheel installer.

## Review and automation

Keep pull-request validation unprivileged. Never use pull-request-provided code or manifests in a workflow with publication secrets. Release automation may propose records; it must not approve its own changes, select its own trust tier, or replace catalog ownership. Signing and publication run only after reviewed changes enter the protected branch.
