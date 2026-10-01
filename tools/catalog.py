"""Validate catalog source entries and build unsigned JSON without network access."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version


ROOT = Path(__file__).resolve().parents[1]
NATIVE_ARCHITECTURES = {
    "deb": {"all": "all", "amd64": "x86_64", "arm64": "aarch64",
            "armhf": "armv7l", "i386": "x86", "riscv64": "riscv64"},
    "rpm": {"noarch": "all", "x86_64": "x86_64", "aarch64": "aarch64",
            "armv7hl": "armv7l", "i686": "x86", "riscv64": "riscv64"},
}
NATIVE_DISTROS = {
    "deb": {"debian", "ubuntu", "raspbian"},
    "rpm": {"fedora", "rhel", "rocky", "almalinux", "opensuse-leap"},
}
HOST_ARCHITECTURES = {"x86_64", "aarch64", "armv7l", "x86", "riscv64"}


def read_json(path: Path) -> dict:
    """Read JSON, refusing ambiguous duplicate object keys."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check_url(value: str) -> None:
    """Reject non-HTTPS URLs, credentials and mutable download selectors."""
    parts = urlsplit(value)
    path = unquote(parts.path)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.port not in (None, 443)
        or parts.query
        or parts.fragment
        or "\\" in value
        or any(char.isspace() or ord(char) < 32 for char in value)
        or any(segment in (".", "..", "latest") for segment in path.lower().split("/"))
    ):
        raise ValueError("URLs must use HTTPS without credentials, query, fragment or latest selectors")


def platform_for_tag(platform: str) -> str:
    """Map supported wheel platform families to catalog target names."""
    if platform == "any":
        return "all"
    for prefix, target in (
        ("manylinux", "linux"),
        ("musllinux", "linux"),
        ("linux_", "linux"),
        ("macosx_", "macos"),
        ("win", "windows"),
    ):
        if platform.startswith(prefix):
            return target
    raise ValueError(f"Unsupported wheel platform: {platform}")


def architectures_for_tag(platform: str) -> set[str]:
    """Normalize supported wheel architecture tags; refuse unknown ABIs."""
    if platform == "any":
        return {"all"}
    if platform.startswith("macosx_") and platform.endswith("_universal2"):
        return {"x86_64", "aarch64"}
    if platform == "win32":
        return {"x86"}
    for suffix, architecture in (
        ("x86_64", "x86_64"), ("amd64", "x86_64"), ("aarch64", "aarch64"),
        ("arm64", "aarch64"), ("armv7l", "armv7l"), ("i686", "x86"),
        ("i386", "x86"), ("riscv64", "riscv64"),
    ):
        if platform.endswith("_" + suffix):
            return {architecture}
    raise ValueError(f"Unsupported wheel architecture: {platform}")


def check_all(values: list[str], label: str) -> set[str]:
    result = set(values)
    if "all" in result and len(result) != 1:
        raise ValueError(f"all cannot be combined with specific {label}")
    return result


def artifact_supports_target(release: dict, artifact: dict, *, platform: str,
                             architecture: str, package_format: str,
                             distro_id: str = "", distro_version: str = "") -> bool:
    """Reference target filter for validated records; NOT an install authorization.

    The future server must additionally check trust, versions, wheel tags,
    dependencies, package ownership, withdrawal and update policy. Callers supply
    the server's userspace architecture, never the app or CPU's architecture.
    """
    if platform not in {"linux", "macos", "windows"} or architecture not in HOST_ARCHITECTURES:
        return False
    if package_format not in {"deb", "rpm", "wheel"} or artifact["format"] != package_format:
        return False
    requires = release["requires"]
    if platform not in requires["platforms"] and "all" not in requires["platforms"]:
        return False
    if artifact["platform"] not in {"all", platform}:
        return False
    for architectures in (requires["architectures"], artifact["architectures"]):
        if architecture not in architectures and "all" not in architectures:
            return False
    if package_format in NATIVE_ARCHITECTURES:
        return platform == "linux" and any(
            target["id"] == distro_id and distro_version in target["versions"]
            for target in artifact["targets"]
        )
    return True


def validate_native_artifact(artifact: dict, distribution: str) -> None:
    """Check declared native identity/targets, not package bytes or executability."""
    package = artifact["package"]
    format_ = artifact["format"]
    architecture = NATIVE_ARCHITECTURES[format_].get(package["architecture"])
    if architecture is None or artifact["architectures"] != [architecture]:
        raise ValueError("Native package architecture must match its canonical architecture")
    if package["name"] != distribution:
        raise ValueError("Native package identity must match catalog distribution")
    native_version = package["version"].split(":", 1)[-1]
    if format_ == "deb":
        filename = f"{package['name']}_{native_version}_{package['architecture']}.deb"
    else:
        if "-" not in native_version:
            raise ValueError("RPM version must include its package release")
        filename = f"{package['name']}-{native_version}.{package['architecture']}.rpm"
    if filename != artifact["filename"]:
        raise ValueError("Native package filename must match its declared identity")
    distro_ids = set()
    for target in artifact["targets"]:
        if target["id"] not in NATIVE_DISTROS[format_]:
            raise ValueError("Distro target is incompatible with package format")
        if target["id"] in distro_ids:
            raise ValueError("Duplicate distro target; combine its versions in one record")
        distro_ids.add(target["id"])


def validate_plugin(plugin: dict, validator: Draft202012Validator) -> None:
    """Validate metadata and release consistency without importing plugin code."""
    validator.validate(plugin)
    check_url(plugin["source"]["repository"])
    for person in [plugin["creator"], *plugin["maintainers"]]:
        check_url(person["url"])
    subdirectory = plugin["source"]["subdirectory"]
    if subdirectory and (
        subdirectory.startswith("/")
        or "\\" in subdirectory
        or ":" in subdirectory
        or any(part in ("", ".", "..") for part in subdirectory.split("/"))
    ):
        raise ValueError("Source subdirectory must be a relative path without traversal")

    versions = set()
    for release in plugin["releases"]:
        version = Version(release["version"])
        if version in versions:
            raise ValueError(f"Duplicate release version: {version}")
        versions.add(version)
        if version.local or (release["channel"] == "stable" and version.is_prerelease):
            raise ValueError("Stable releases must be final; local versions cannot be published")
        if "rollback_versions" in release and not str(SpecifierSet(release["rollback_versions"])):
            raise ValueError("Empty rollback version range")
        check_url(release["release_notes"])
        requires = release["requires"]
        for field in ("server", "sdk", "python", *(["renderer"] if "renderer" in requires else [])):
            if not str(SpecifierSet(requires[field])):
                raise ValueError(f"Empty {field} version range")
        platforms = check_all(requires["platforms"], "required platforms")
        architectures = check_all(requires["architectures"], "required architectures")
        filenames = set()
        for artifact in release["artifacts"]:
            check_url(artifact["url"])
            filename = artifact["filename"]
            if filename in filenames:
                raise ValueError(f"Duplicate artifact filename: {filename}")
            filenames.add(filename)
            if unquote(urlsplit(artifact["url"]).path.rsplit("/", 1)[-1]) != filename:
                raise ValueError("Artifact URL must end with its filename")
            artifact_architectures = check_all(artifact["architectures"], "artifact architectures")
            if "all" not in platforms and artifact["platform"] not in platforms | {"all"}:
                raise ValueError("Artifact target is excluded by required platforms")
            if "all" not in architectures and "all" not in artifact_architectures and not artifact_architectures <= architectures:
                raise ValueError("Artifact architecture is excluded by required architectures")
            if artifact["format"] in NATIVE_ARCHITECTURES:
                validate_native_artifact(artifact, plugin["distribution"])
                continue
            name, wheel_version, _, tags = parse_wheel_filename(filename)
            if name != canonicalize_name(plugin["distribution"]) or wheel_version != version:
                raise ValueError("Wheel identity must match catalog distribution and version")
            targets = {platform_for_tag(tag.platform) for tag in tags}
            if targets != {artifact["platform"]}:
                raise ValueError("Artifact platform must match all wheel platform tags")
            wheel_architectures = set().union(*(architectures_for_tag(tag.platform) for tag in tags))
            if wheel_architectures != artifact_architectures:
                raise ValueError("Artifact architectures must match all wheel architecture tags")
            if artifact["platform"] == "all" and any(tag.abi != "none" for tag in tags):
                raise ValueError("Cross-platform artifacts cannot require a native ABI")


def load_validator(root: Path = ROOT) -> Draft202012Validator:
    """Load and check the local schema; all references remain within it."""
    schema = read_json(root / "schemas" / "plugin.schema.json")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def build_catalog(root: Path = ROOT, revision: str = "local") -> dict:
    """Assemble validated entries from plugins only, with unique identities."""
    if revision != "local" and not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Revision must be local or a full Git commit hash")
    validator = load_validator(root)
    identities = {field: set() for field in ("id", "distribution", "entry_point")}
    plugins = []
    for path in sorted((root / "plugins").glob("*.json")):
        plugin = read_json(path)
        validate_plugin(plugin, validator)
        if path.stem != plugin["id"]:
            raise ValueError(f"Filename must match plugin id: {path.name}")
        for field, known in identities.items():
            value = plugin[field]
            if value in known:
                raise ValueError(f"Duplicate {field}: {value}")
            known.add(value)
        plugin["releases"].sort(key=lambda release: Version(release["version"]), reverse=True)
        for release in plugin["releases"]:
            release["artifacts"].sort(key=lambda artifact: artifact["filename"])
        plugins.append(plugin)
    if not plugins:
        raise ValueError("Catalog must contain at least one plugin")
    return {
        "schema_version": 1,
        "catalog_id": "kalinka",
        "revision": revision,
        "plugins": plugins,
    }


def main() -> None:
    """Validate inputs and write the requested unsigned catalog artifact."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="local")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Check the public feed matches reviewed source entries without writing it")
    args = parser.parse_args()
    if args.check:
        published = read_json(args.output)
        expected = build_catalog(revision=published["revision"])
        if published != expected:
            raise ValueError("Public catalog is stale; rebuild catalog.json from plugins/")
        print(f"Public catalog matches {len(expected['plugins'])} reviewed entries")
        return
    catalog = build_catalog(revision=args.revision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Validated {len(catalog['plugins'])} entries; wrote unsigned catalog to {args.output}")


if __name__ == "__main__":
    main()
