---
description: HarmonyOS ArkUI UI 设计与交互规范（弹层/顶栏/加载态/图标语义，事前约束，避免 bindSheet 重叠等坑）
paths:
  - "**/*.ets"
---

# ArkUI UI 设计规范

与 `dwy-arkts-ui-build.md`（怎么编译/踩过哪些 API 坑）配套：本文件管 **长什么样、交互怎么关、加载怎么显**。
写页面 / sheet **先按本规范搭骨架**，再写业务。踩到新 UI 坑：先记 `dwy-harmony-pitfalls.md`，再回写本文件。

## 1. 分层约定

| 层 | 职责 | 典型 API |
|---|---|---|
| 系统 chrome | 系统提供的关闭/拖拽指示 | `bindSheet` 的 `showClose`、下拉关闭 |
| 内容顶栏 | 标题 + 业务操作 +（可选）自绘关闭 | `SheetHeader` / 自绘 `Row` |
| 内容区 | 表单、列表、图 | 业务组件 |

**硬规则：系统关闭钮与内容自绘「关弹层」× 禁止同时出现。**

## 2. bindSheet 关闭策略（二选一）

### 2.1 模式 A：自绘关闭（工具页 / 表单 / 顶栏有右侧操作）

适用：Shell、进程、性能、调试、代理、录屏、快捷指令、设备编辑、**配对弹层**、设备信息（有「复制全部」等）。

```ets
.bindSheet(this.open, this.content(), {
  detents: [SheetSize.LARGE],
  backgroundColor: Palette.device,
  showClose: false, // 必须关系统 ×
  onDisappear: () => { this.open = false; },
})

@Builder
content(): void {
  FooPage({ onClose: () => { this.open = false; } })
}
```

内容顶栏结构（从左到右）：

```
[ 标题（layoutWeight 1，单行省略） ] [ 可选业务按钮 ] [ 关闭 × ]
```

- 关闭用 `sys.symbol.xmark`，固定触控约 `36×36`，勿与分段按钮同一 `Row` 抢宽。
- 分段 / Tab 切换放在 **顶栏下一行**，整行 `width('100%')`，不得伸进系统 chrome 区域。

### 2.2 模式 B：仅系统关闭（纯浏览 / 轻列表）

适用：语言选择、截图预览、无业务顶栏操作的列表。

```ets
.bindSheet(this.open, this.content(), {
  showClose: true,
  onDisappear: () => { this.open = false; },
})
```

- 内容 **禁止** 再画关闭 ×。
- 顶栏右侧 **禁止** 放会与系统 × 重叠的控件（可放在内容区下方或用「完成」文字按钮在底部）。

### 2.3 禁止

| 禁止 | 原因 |
|---|---|
| `showClose: true` + `SheetHeader` / 自绘 × | 双 × 重叠 |
| `showClose` 省略 + 自绘 × | 默认常带系统 ×，仍重叠 |
| 系统 × 与「新增 / 复制全部 / 分段 Tab」同一视觉行 | 贴边、难点 |
| 关闭回调空实现（`onClose` 未注入） | × 点了无反应 |

## 3. 图标语义（禁止混用）

| 语义 | 推荐符号 | 禁止 |
|---|---|---|
| 关弹层 | `xmark`（顶栏） | 与「清空」共用同一位置无说明 |
| 清空输入 | `xmark_circle_fill`（输入框旁） | 当成关 sheet |
| 返回上一页 | `chevron_left`（`PageHeaderBar`） | 用 × 表示返回 |
| 删除 | `trash` | 用 × 表示删除条目 |

输入弹层（键盘）：**关 sheet 用模式 B（系统 ×）**；清空用输入框旁圆形 ×，注释写明「清空非关闭」。

## 4. 加载与空态（禁止永久 spinner）

异步出图 / 出列表必须三态：

| 状态 | UI |
|---|---|
| 加载中 | `LoadingProgress`（限在固定占位区域内） |
| 成功 | 内容（图 / 列表） |
| 失败 | 文案说明 + 可选重试；**禁止**继续转圈 |

二维码 / 图片：

1. 优先系统能力（如 ScanKit）。
2. 失败必须有 **可见兜底**（纯逻辑绘制 / 占位文案），不能空白。
3. 占位区 **固定宽高**，避免生成前后布局跳动。

## 5. 顶栏与安全区

- **Push 页**：`PageHeaderBar`（返回 + 标题 + trailing），前景在安全区内。
- **Sheet**：见 §2；全屏背景可用，主交互勿进系统手势死角。
- 标题：`maxLines(1)` + `TextOverflow.Ellipsis`，避免长文案挤掉按钮。
- 触控目标：主要按钮高度建议 ≥ 40；图标按钮约 36×36。

## 6. 布局与间距（基线）

- 页面水平 padding 统一 **16 / 20**（工具页内容区常用 16–20）。
- 卡片圆角与描边走 **设计 token**（如 `Palette.surface2` + `hairline`），禁止业务页散落硬编码色。
- 列表/宫格：用 `List` / `Grid` + 间距系统，不用绝对 `offset` 拼主布局。
- 固定视觉比例控件（二维码、D-pad）可用固定边长，**外层容器仍自适应宽度**。

## 7. 颜色与动效

- 颜色只从 `Palette`（或项目 token）取，禁止裸 `0xFF...` 散落业务页（生成图 RGBA 缓冲区除外）。
- 动效优先项目统一 spring / 系统默认；新增动画参数与现有 `Motion` 一致。
- 强调色用于主按钮；关闭/次要操作用 `Palette.sub`，删除用 `Palette.red`。

## 8. 文案与国际化

- 所有用户可见文案走 `loc('key')` + 资源表，禁止硬编码中文/英文（调试日志除外）。
- 新 key 至少补齐 **开发语言 + en**；其它语言可后续补。

## 9. 自检清单（PR / 提交前）

- [ ] 每个 `bindSheet` 已显式 `showClose: true` 或 `false`（不省略）。
- [ ] 自绘 × 的 sheet 已 `showClose: false` 且 `onClose` 接通。
- [ ] 系统 × 的 sheet 内容无第二颗关闭钮、右侧无抢位控件。
- [ ] 异步区有失败态，无永久 spinner。
- [ ] 出码/出图有 ScanKit 失败兜底（若依赖）。
- [ ] 图标名在 `id_defined.json` 存在（见 ui-build §1）。
- [ ] 文案全部 `loc`。

## 10. 与 iOS 对照时注意

- iOS `sheet` + 导航栏 toolbar 关闭 ≠ 鸿蒙默认 `showClose`；移植时 **重新选 §2 模式**，不要两端各画一套再叠系统。
- SF Symbols 名不能直接当 `sys.symbol`（见 ui-build §1）。
