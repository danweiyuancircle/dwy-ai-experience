# DesignCore 动效测试

运行：`swift test --filter MotionTests`。

| 用例 | 边界 |
| --- | --- |
| `testReducedMotionDisablesEveryPresetAnimation` | 所有预设遵循系统减少动态效果，正常模式有动画 |
| `testSemanticPresetsReuseExistingMotionTokens` | 语义预设复用已有统一参数，不改变旧调用节奏 |
| `testReducedTransitionsKeepFadeAndRemoveMovement` | 轻位移在减少动态效果下变为纯淡入淡出 |
| `testPublicModifiersAndLegacyPressStyleRemainComposable` | 新公开修饰器与旧按压 API 可组合编译；系统减少动态效果环境是只读值，不伪造注入 |
