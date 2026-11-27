"""所有 Apple 默认展示使用同一份公开的共享素材，避免新分类落回历史目录。"""

from importlib import import_module

import pytest


@pytest.mark.parametrize("module,name,icon", [
    ("providers.apple_appearance", "DEFAULT_APPEARANCE", "purchase"),
    ("providers.apple_appearance", "BUYOUT_APPEARANCE", "purchase"),
    ("providers.apple_appearance", "SUBSCRIPTION_APPEARANCE", "subscription"),
    ("providers.apple_appearance", "REFUND_APPEARANCE", "refund"),
    ("providers.apple_appearance", "ACTIVITY_APPEARANCE", "general"),
    ("providers.asc_appearance", "DEFAULT_APPEARANCE", "review"),
    ("analytics.appearance", "DEFAULT_APPEARANCE", "report"),
    ("reviews.appearance", "DEFAULT_APPEARANCE", "general"),
    ("ratings.appearance", "DEFAULT_APPEARANCE", "report"),
])
def test_all_apple_presets_use_published_shared_icons(module, name, icon):
    preset = getattr(import_module(f"dwy_apple_notify.{module}"), name)
    assert preset.avatar_url == (
        "https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/"
        f"8c86735ec6bcfeee24f101fdccbc900b9d7bc2dd/assets/notification-icons/{icon}.png"
    )


def test_renewal_icon_matches_subscription_style():
    import struct
    from pathlib import Path
    from xml.etree import ElementTree

    assets = Path(__file__).resolve().parents[4] / "assets" / "notification-icons"
    subscription = ElementTree.parse(assets / "subscription.svg").getroot()
    renewal = ElementTree.parse(assets / "renewal.svg").getroot()
    assert renewal.attrib == subscription.attrib
    assert renewal[0].attrib == subscription[0].attrib
    assert renewal[1].attrib == subscription[1].attrib
    assert ElementTree.tostring(renewal[1]) != ElementTree.tostring(subscription[1])
    png = (assets / "renewal.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (256, 256)


def test_renewal_preset_uses_published_shared_icon():
    from dwy_apple_notify.providers.apple_appearance import RENEWAL_APPEARANCE

    assert RENEWAL_APPEARANCE.avatar_url == (
        "https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/"
        "d6c1b5145ee0a3a13e0a919463d56a0a1469100d/assets/notification-icons/renewal.png"
    )
