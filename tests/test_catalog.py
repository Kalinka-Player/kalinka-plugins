"""Contract checks for catalog metadata and release artifact selection inputs."""

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from catalog import (ROOT, artifact_supports_target, build_catalog, check_url,
                     load_validator, read_json, validate_plugin)


class CatalogTests(unittest.TestCase):
    """Exercise malformed releases and catalog identity collisions."""

    def setUp(self):
        self.validator = load_validator()
        self.plugin = read_json(ROOT / "examples" / "example-plugin.json")
        self.release = self.plugin["releases"][0]
        self.artifact = self.release["artifacts"][0]

    def validate(self):
        validate_plugin(self.plugin, self.validator)

    def rename_wheel(self, filename):
        self.artifact["filename"] = filename
        self.artifact["url"] = "https://example.invalid/releases/v1.2.0/" + filename

    def test_cross_platform_example(self):
        self.validate()

    def test_seed_catalog_has_no_fake_releases_or_example(self):
        catalog = build_catalog()
        self.assertEqual({entry["id"] for entry in catalog["plugins"]}, {
            "dummydevice", "jamendo", "localfiles", "musiccast", "upnp", "spotify", "qobuz", "roon",
        })
        self.assertTrue(all(entry["releases"] == [] for entry in catalog["plugins"]
                            if entry["delivery"] == "bundle"))
        self.assertEqual({entry["id"] for entry in catalog["plugins"] if entry["releases"]},
                         {"spotify", "qobuz"})
        self.assertEqual({entry["id"] for entry in catalog["plugins"] if entry["delivery"] == "bundle"}, {
            "dummydevice", "jamendo", "localfiles", "musiccast", "upnp",
        })
        self.assertEqual(catalog, build_catalog())

    def test_public_feed_matches_reviewed_entries(self):
        published = read_json(ROOT / "catalog.json")
        self.assertEqual(published, build_catalog(revision=published["revision"]))
        self.assertEqual(published["catalog_id"], "kalinka")

    def test_only_jamendo_and_localfiles_are_official(self):
        plugins = build_catalog()["plugins"]
        official = {"jamendo", "localfiles"}
        self.assertEqual({p["id"] for p in plugins if p["tier"] == "official"}, official)
        for plugin in plugins:
            with self.subTest(plugin=plugin["id"]):
                self.assertEqual(plugin["tier"],
                                 "official" if plugin["id"] in official else "unofficial")

    def test_native_platform_cannot_be_all(self):
        self.rename_wheel("kalinka_plugin_example_radio-1.2.0-cp311-cp311-manylinux_2_28_aarch64.whl")
        with self.assertRaisesRegex(ValueError, "platform"):
            self.validate()
        self.artifact["platform"] = "linux"
        self.artifact["architectures"] = ["aarch64"]
        self.validate()

    def test_seed_types_match_sdk_plugin_families(self):
        self.assertEqual({entry["id"]: entry["type"] for entry in build_catalog()["plugins"]}, {
            "localfiles": "input_module",
            "jamendo": "input_module",
            "upnp": "input_module",
            "musiccast": "output_device",
            "dummydevice": "output_device",
            "spotify": "input_module",
            "qobuz": "input_module",
            "roon": "input_module",
        })

    def test_spotify_and_qobuz_are_unofficial_independent_inputs(self):
        entries = {p["id"]: p for p in build_catalog()["plugins"]}
        for plugin_id, license_id in (("spotify", "MIT"), ("qobuz", "Apache-2.0")):
            with self.subTest(plugin_id=plugin_id):
                plugin = entries[plugin_id]
                self.assertEqual(plugin["tier"], "unofficial")
                self.assertEqual(plugin["type"], "input_module")
                self.assertEqual(plugin["delivery"], "independent")
                self.assertEqual(plugin["license"], license_id)
                self.assertEqual(plugin["distribution"], f"kalinka-plugin-{plugin_id}")
                self.assertEqual(plugin["entry_point"], f"kalinka_plugin_{plugin_id}")
                self.assertEqual(plugin["source"], {
                    "repository": f"https://github.com/Kalinka-Player/kalinka-plugin-{plugin_id}",
                    "subdirectory": "",
                })
                self.assertEqual(len(plugin["releases"]), 1)
                self.assertEqual(plugin["releases"][0]["data_rollback"], "manual")

    def test_plugin_type_is_required_even_with_category_tags(self):
        del self.plugin["type"]
        self.plugin["categories"] = ["music-source"]
        with self.assertRaises(ValidationError):
            self.validate()

    def test_seed_requirements_use_versions_not_source_commits(self):
        entries = {p["id"]: p for p in build_catalog()["plugins"]}
        spotify = entries["spotify"]["releases"][0]
        self.assertEqual(spotify["requires"]["server"], ">=5.3,<6")
        self.assertEqual(spotify["requires"]["renderer"], ">=0.5,<1")
        for plugin in entries.values():
            for release in plugin["releases"]:
                with self.subTest(plugin=plugin["id"], version=release["version"]):
                    self.assertNotRegex(json.dumps(release["requires"]),
                                        r"(?i)\bcommits?\b|\b[0-9a-f]{40}\b")
                    self.assertRegex(release["source_commit"], r"^[0-9a-f]{40}$")

    def test_only_sdk_plugin_type_values_are_accepted(self):
        for value in ("input_module", "output_device"):
            with self.subTest(value=value):
                self.plugin["type"] = value
                if value == "output_device":
                    self.plugin["device_support"] = self.device_support()
                self.validate()
        for value in ("input-source", "device-control", "", None, ["input_module"], 1):
            with self.subTest(value=value):
                self.plugin["type"] = value
                with self.assertRaises(ValidationError):
                    self.validate()

    def test_category_tags_do_not_determine_plugin_type(self):
        self.plugin["categories"] = []
        self.validate()
        self.plugin["categories"] = ["future-search-tag"]
        self.validate()

    @staticmethod
    def device_support():
        return {"models": [], "families": ["Example Audio Demo Network Control"],
                "notes": ["Synthetic family only; local network control required."]}

    def test_output_device_requires_support_information(self):
        self.plugin["type"] = "output_device"
        with self.assertRaises(ValidationError):
            self.validate()
        self.plugin["device_support"] = self.device_support()
        self.validate()

    def test_device_support_accepts_models_families_or_both(self):
        self.plugin["type"] = "output_device"
        for models, families in ((["Example AVR 100"], []), ([], ["Demo family"]),
                                 (["Example AVR 100"], ["Demo family"])):
            with self.subTest(models=models, families=families):
                self.plugin["device_support"] = {"models": models, "families": families,
                                                 "notes": ["Example hardware requirements."]}
                self.validate()

    def test_empty_blank_duplicate_or_malformed_device_support_is_rejected(self):
        self.plugin["type"] = "output_device"
        invalid = [
            {},
            {"models": [], "families": [], "notes": ["Unknown"]},
            {"models": [], "families": [" "], "notes": ["Example"]},
            {"models": [""], "families": [], "notes": ["Example"]},
            {"models": ["Demo", "Demo"], "families": [], "notes": ["Example"]},
            {"models": [], "families": ["Demo", "Demo"], "notes": ["Example"]},
            {"models": [], "families": ["Demo"], "notes": []},
            {"models": [], "families": ["Demo"], "notes": ["\t"]},
            {"models": "Demo", "families": [], "notes": ["Example"]},
            {"models": [], "families": ["Demo"], "notes": ["Example"], "probe_command": "run"},
        ]
        for support in invalid:
            with self.subTest(support=support), self.assertRaises(ValidationError):
                self.plugin["device_support"] = support
                self.validate()

    def test_input_module_does_not_claim_device_support(self):
        self.plugin["device_support"] = self.device_support()
        with self.assertRaises(ValidationError):
            self.validate()

    def test_device_example_is_valid_and_excluded_from_catalog(self):
        plugin = read_json(ROOT / "examples" / "example-device-plugin.json")
        validate_plugin(plugin, self.validator)
        self.assertNotIn(plugin["id"], {entry["id"] for entry in build_catalog()["plugins"]})

    def test_output_seed_support_survives_catalog_build(self):
        devices = {p["id"]: p["device_support"] for p in build_catalog()["plugins"]
                   if p["type"] == "output_device"}
        self.assertEqual(devices["musiccast"]["models"], [])
        self.assertEqual(devices["musiccast"]["families"], ["Yamaha MusicCast / Yamaha Extended Control"])
        self.assertEqual(devices["dummydevice"]["families"], ["Kalinka simulated devices"])

    def test_artifact_target_must_be_in_required_platforms(self):
        self.rename_wheel("kalinka_plugin_example_radio-1.2.0-cp311-cp311-win_amd64.whl")
        self.artifact["platform"] = "windows"
        self.release["requires"]["platforms"] = ["linux"]
        with self.assertRaisesRegex(ValueError, "excluded"):
            self.validate()

    def test_unsupported_schema_or_unknown_fields(self):
        for field, value in (("schema_version", 2), ("install_command", "some-command")):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.plugin)
                altered[field] = value
                with self.assertRaises(ValidationError):
                    validate_plugin(altered, self.validator)

    def test_invalid_or_empty_ranges(self):
        for value in ("3.6 or later", " "):
            with self.subTest(value=value):
                self.release["requires"]["sdk"] = value
                with self.assertRaises(ValueError):
                    self.validate()

    def test_wheel_must_match_distribution_and_version(self):
        for filename in (
            "different_plugin-1.2.0-py3-none-any.whl",
            "kalinka_plugin_example_radio-1.3.0-py3-none-any.whl",
        ):
            with self.subTest(filename=filename):
                self.rename_wheel(filename)
                with self.assertRaisesRegex(ValueError, "identity"):
                    self.validate()

    def test_prerelease_requires_preview(self):
        self.release["version"] = "1.2.0rc1"
        self.rename_wheel("kalinka_plugin_example_radio-1.2.0rc1-py3-none-any.whl")
        with self.assertRaisesRegex(ValueError, "final"):
            self.validate()
        self.release["channel"] = "preview"
        self.validate()

    def test_duplicate_versions_use_pep440_equality(self):
        duplicate = copy.deepcopy(self.release)
        duplicate["version"] = "1.2.0.0"
        self.plugin["releases"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate release"):
            self.validate()

    def test_withdrawal_requires_reason(self):
        self.release["withdrawn"] = True
        with self.assertRaises(ValidationError):
            self.validate()
        self.release["withdrawal_reason"] = "Broken startup on a supported platform"
        self.validate()

    def test_automatic_rollback_needs_an_explicit_version_range(self):
        del self.release["rollback_versions"]
        with self.assertRaises(ValidationError):
            self.validate()
        self.release["data_rollback"] = "manual"
        self.validate()
        self.release["rollback_versions"] = ">=1.1"
        with self.assertRaises(ValidationError):
            self.validate()

    def test_integrity_fields_are_required(self):
        for field, value in (("sha256", "not-a-sha256"), ("size_bytes", 0)):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.plugin)
                altered["releases"][0]["artifacts"][0][field] = value
                with self.assertRaises(ValidationError):
                    validate_plugin(altered, self.validator)

    def test_credentialed_mutable_and_non_https_urls_are_rejected(self):
        for url in (
            "http://example.invalid/file.whl",
            "https://user:secret@example.invalid/file.whl",
            "https://example.invalid/file.whl?token=secret",
            "https://example.invalid/releases/latest/download/file.whl",
            "https://example.invalid/releases/%6catest/file.whl",
            "https://example.invalid/file.whl#fragment",
            "file:///tmp/plugin.whl",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                check_url(url)

    def test_source_subdirectory_cannot_escape_repo(self):
        for subdirectory in ("../plugin", "/plugin", "plugins/../other", "C:\\plugin"):
            with self.subTest(subdirectory=subdirectory):
                self.plugin["source"]["subdirectory"] = subdirectory
                with self.assertRaisesRegex(ValueError, "relative path"):
                    self.validate()

    def test_duplicate_distribution_is_rejected_across_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "schemas", root / "schemas")
            (root / "plugins").mkdir()
            for plugin_id in ("one", "two"):
                entry = copy.deepcopy(self.plugin)
                entry["id"] = plugin_id
                (root / "plugins" / f"{plugin_id}.json").write_text(json.dumps(entry))
            with self.assertRaisesRegex(ValueError, "Duplicate distribution"):
                build_catalog(root)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "entry.json"
            path.write_text('{"id":"one","id":"two"}')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                read_json(path)

    def native_example(self, plugin_id="spotify", format_="deb", architecture="x86_64"):
        plugin = read_json(ROOT / "plugins" / f"{plugin_id}.json")
        self.plugin = plugin
        self.release = plugin["releases"][0]
        self.artifact = next(a for a in self.release["artifacts"]
                             if a["format"] == format_ and architecture in a["architectures"])
        self.release["artifacts"] = [self.artifact]

    def test_architecture_is_required_on_release_and_artifact(self):
        for record in (self.release["requires"], self.artifact):
            architectures = record.pop("architectures")
            with self.assertRaises(ValidationError):
                self.validate()
            record["architectures"] = architectures

    def test_all_cannot_be_mixed_with_specific_architectures(self):
        for record in (self.release["requires"], self.artifact):
            record["architectures"] = ["all", "aarch64"]
            with self.assertRaisesRegex(ValueError, "all cannot"):
                self.validate()
            record["architectures"] = ["all"]

    def test_wheel_architecture_must_match_tags(self):
        self.artifact["platform"] = "linux"
        self.artifact["architectures"] = ["x86_64"]
        self.rename_wheel("kalinka_plugin_example_radio-1.2.0-cp311-cp311-manylinux_2_28_aarch64.whl")
        with self.assertRaisesRegex(ValueError, "architecture tags"):
            self.validate()
        self.artifact["architectures"] = ["aarch64"]
        self.validate()

    def test_universal2_requires_both_architectures(self):
        self.artifact["platform"] = "macos"
        self.artifact["architectures"] = ["x86_64", "aarch64"]
        self.rename_wheel("kalinka_plugin_example_radio-1.2.0-cp311-cp311-macosx_11_0_universal2.whl")
        self.validate()
        self.artifact["architectures"] = ["aarch64"]
        with self.assertRaisesRegex(ValueError, "architecture tags"):
            self.validate()

    def test_deb_and_rpm_cannot_claim_cross_platform(self):
        for format_ in ("deb", "rpm"):
            self.native_example(format_=format_)
            self.artifact["platform"] = "all"
            with self.assertRaises(ValidationError):
                self.validate()

    def test_native_architecture_identity_must_agree(self):
        for format_ in ("deb", "rpm"):
            self.native_example(format_=format_)
            for value in (["all"], ["aarch64"], ["x86_64", "aarch64"]):
                self.artifact["architectures"] = value
                with self.assertRaisesRegex(ValueError, "architecture"):
                    self.validate()

    def test_native_package_and_distro_information_required(self):
        for field in ("package", "targets"):
            self.native_example()
            del self.artifact[field]
            with self.assertRaises(ValidationError):
                self.validate()

    def test_package_format_must_match_distro(self):
        self.native_example()
        self.artifact["targets"] = [{"id": "fedora", "versions": ["44"]}]
        with self.assertRaisesRegex(ValueError, "Distro"):
            self.validate()

    def test_duplicate_distro_records_are_rejected(self):
        self.native_example()
        self.artifact["targets"].append({"id": "debian", "versions": ["12"]})
        with self.assertRaisesRegex(ValueError, "Duplicate distro"):
            self.validate()

    def test_unknown_or_wildcard_distro_versions_are_rejected(self):
        for versions in ([], ["all"], ["13+"], ["*"], ["13", "13"]):
            self.native_example()
            self.artifact["targets"][0]["versions"] = versions
            with self.assertRaises(ValidationError):
                self.validate()

    def test_release_architecture_restricts_artifacts(self):
        self.native_example()
        self.release["requires"]["architectures"] = ["aarch64"]
        with self.assertRaisesRegex(ValueError, "excluded"):
            self.validate()

    def test_native_filename_must_match_package_identity(self):
        self.native_example()
        self.artifact["package"]["version"] = "0.3.0"
        with self.assertRaisesRegex(ValueError, "filename"):
            self.validate()

    def test_native_package_cannot_impersonate_another_distribution(self):
        self.native_example()
        self.artifact["package"]["name"] = "another-package"
        with self.assertRaisesRegex(ValueError, "identity"):
            self.validate()

    def supports(self, **overrides):
        target = dict(platform="linux", architecture="x86_64", package_format="deb",
                      distro_id="debian", distro_version="13")
        target.update(overrides)
        return artifact_supports_target(self.release, self.artifact, **target)

    def test_spotify_target_matching_fails_closed(self):
        self.native_example()
        self.assertTrue(self.supports())
        self.assertTrue(self.supports(distro_id="ubuntu", distro_version="24.04"))
        for target in (
            {"architecture": "aarch64"}, {"architecture": "armv7l"},
            {"architecture": "unknown"}, {"architecture": "all"},
            {"platform": "windows"}, {"platform": "all"},
            {"package_format": "rpm"}, {"package_format": "unknown"},
            {"distro_id": "fedora"}, {"distro_id": "dietpi"},
            {"distro_version": "14"}, {"distro_version": ""},
        ):
            with self.subTest(target=target):
                self.assertFalse(self.supports(**target))

    def test_rpm_target_requires_exact_distro_and_architecture(self):
        self.native_example(format_="rpm", architecture="aarch64")
        target = dict(package_format="rpm", architecture="aarch64",
                      distro_id="fedora", distro_version="44")
        self.assertTrue(self.supports(**target))
        self.assertFalse(self.supports(**{**target, "distro_version": "45"}))
        self.assertFalse(self.supports(**{**target, "architecture": "x86_64"}))

    def test_all_deb_does_not_mean_all_platforms(self):
        self.native_example(plugin_id="qobuz", architecture="all")
        for architecture in ("x86_64", "aarch64", "armv7l"):
            self.assertTrue(self.supports(architecture=architecture))
        for target in ({"platform": "macos"}, {"platform": "windows"},
                       {"package_format": "rpm"}, {"distro_id": "fedora"}):
            self.assertFalse(self.supports(**target))
        self.release["requires"]["architectures"] = ["aarch64"]
        self.assertFalse(self.supports())
        self.assertTrue(self.supports(architecture="aarch64"))

    def test_cross_platform_wheel_still_obeys_release_restrictions(self):
        for platform in ("linux", "macos", "windows"):
            self.assertTrue(self.supports(platform=platform, package_format="wheel"))
        self.release["requires"]["platforms"] = ["linux"]
        self.assertFalse(self.supports(platform="macos", package_format="wheel"))


if __name__ == "__main__":
    unittest.main()
