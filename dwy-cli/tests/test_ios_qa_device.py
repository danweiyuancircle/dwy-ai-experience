import runpy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = (Path(__file__).resolve().parents[1]
          / "templates/ai-tools/skills/Apple/dwy-apple-local-debug/scripts/ios_qa_device.py")
RESOLVE = runpy.run_path(str(SCRIPT))["resolve_device"]
UDID = "941B37E2-F6F2-4F8B-AFB9-408846452530"
RUNTIME_PREFIX = "com.apple.CoreSimulator.SimRuntime.iOS-"
TYPE_PREFIX = "com.apple.CoreSimulator.SimDeviceType.iPhone-"


def runtime(version, *models, available=True, suffix=""):
    return {
        "identifier": RUNTIME_PREFIX + version.replace(".", "-") + suffix,
        "version": version,
        "isAvailable": available,
        "supportedDeviceTypes": [
            {"name": f"iPhone {model}", "identifier": TYPE_PREFIX + model.replace(" ", "-")}
            for model in models
        ],
    }


class IOSQADeviceTests(unittest.TestCase):
    def resolve(self, major, runtimes, devices, *expected_create):
        simctl = Mock(return_value=UDID)
        with patch.dict(RESOLVE.__globals__, {
            "_inventory": lambda: {"runtimes": runtimes, "devices": devices},
            "_simctl": simctl,
        }):
            try:
                return RESOLVE(major)
            finally:
                if expected_create:
                    simctl.assert_called_once_with("create", *expected_create)
                else:
                    simctl.assert_not_called()

    def test_reuses_older_runtime_and_same_udid(self):
        older, newer = runtime("27.0", "17"), runtime("27.2", "16")
        devices = {older["identifier"]: [{"name": "IOS27-QA", "udid": UDID, "isAvailable": True}]}
        for _ in range(2):
            self.assertEqual(self.resolve(27, [newer, older], devices), (UDID, "27.0", False))

    def test_creates_on_newest_compatible_runtime_and_prefers_iphone_16(self):
        specialized = runtime("27.11", "17 Pro", suffix="-Special")
        latest = runtime("27.10", "17", "16")
        older = runtime("27.9", "16")
        self.assertEqual(self.resolve(
            27, [older, latest, specialized], {}, "IOS27-QA", TYPE_PREFIX + "16", latest["identifier"],
        ), (UDID, "27.10", True))

    def test_uses_compatible_standard_model_when_iphone_16_is_unavailable(self):
        target = runtime("26.5", "18 Pro", "17", "15")
        self.assertEqual(self.resolve(
            26, [target], {}, "IOS26-QA", TYPE_PREFIX + "17", target["identifier"],
        ), (UDID, "26.5", True))

    def test_rejects_conflicting_or_unavailable_devices_without_creating(self):
        right, wrong = runtime("18.6", "16"), runtime("26.5", "16")
        device = {"name": "IOS18-QA", "udid": UDID, "isAvailable": True}
        for devices, message in [
            ({right["identifier"]: [device, device]}, "同名"),
            ({wrong["identifier"]: [device]}, "不属于 iOS 18"),
            ({right["identifier"]: [dict(device, isAvailable=False)]}, "不可用"),
        ]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.resolve(18, [right, wrong], devices)

    def test_explains_missing_runtime_and_missing_standard_model(self):
        with self.assertRaisesRegex(ValueError, "缺少可用的 iOS 18 runtime"):
            self.resolve(18, [runtime("18.6", "16", available=False)], {})
        with self.assertRaisesRegex(ValueError, "没有兼容的标准版 iPhone"):
            self.resolve(18, [runtime("18.6", "16 Pro")], {})


if __name__ == "__main__":
    unittest.main()
