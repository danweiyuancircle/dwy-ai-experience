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
