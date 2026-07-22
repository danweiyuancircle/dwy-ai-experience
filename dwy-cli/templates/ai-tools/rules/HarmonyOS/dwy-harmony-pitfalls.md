---
description: 鸿蒙踩坑四栏归档（现象/根因/正确做法/适用）。事前规范见 dwy-arkts-ui-design / dwy-arkts-ui-build / dwy-arkts-strict
paths:
  - "**/*.ets"
  - "**/build-profile.json5"
---

# 鸿蒙开发坑清单（归档）

> **事前约束**请先读：
>
> | 文件 | 用途 |
> |---|---|
> | `dwy-arkts-strict.md` | 语言禁用语法 |
> | `dwy-arkts-ui-build.md` | 组件 API / 构建 / 设备与运行时 |
> | `dwy-arkts-ui-design.md` | UI 弹层/顶栏/加载态规范 |
>
> 本文件只记 **已踩过的坑**（四栏）。新坑：先按格式追加 → 再把「正确做法」回写到对应规范文件，避免规范与归档脱节。

## 分类索引

- ArkUI 弹层 / 出码
- 工程与设备网络

---

## ArkUI 弹层 / 出码

### bindSheet 系统 × 与内容自绘 × / 顶栏按钮重叠

- **现象**：右上两颗 ×，或系统 × 与「扫码/配对码」「新增」「复制全部」贴在一起。
- **根因**：`showClose` 与内容自绘关闭/右侧操作同区叠放。
- **正确做法**：见 `dwy-arkts-ui-design.md` §2（二选一）；禁止省略 `showClose`。
- **适用**：所有 `bindSheet`。

### 内容区 × 是清空不是关 sheet

- **现象**：键盘输入框旁 × 被当成关弹层。
- **根因**：语义是清空输入。
- **正确做法**：见 `dwy-arkts-ui-design.md` §3。
- **适用**：Keyboard / 搜索。

### ScanKit 二维码模拟器空白 + 永久 spinner

- **现象**：配对扫码页只转圈，无码图。
- **根因**：HVD 上 `generateBarcode` 常失败；失败 UI 仍 loading。
- **正确做法**：见 `dwy-arkts-ui-build.md` §14 + `dwy-arkts-ui-design.md` §4（兜底出图 + 三态）。
- **适用**：出码展示。

---

## 工程与设备网络

### unsigned.hap 真机装不上

- **现象**：CLI 打包成功，真机安装失败。
- **根因**：未配置 `signingConfigs`。
- **正确做法**：见 `dwy-arkts-ui-build.md` §11。
- **适用**：真机分发。

### 模拟器代理设置无法让 ADB 连局域网电视

- **现象**：在 HVD「代理设置」里配代理/DNS，仍连不上 `192.168.x.x:5555`。
- **根因**：代理只走 HTTP 出网；app 用原始 TCP；HVD 为 NAT 非 LAN peer。
- **正确做法**：见 `dwy-arkts-ui-build.md` §13；真机同 Wi-Fi。
- **适用**：局域网调试类产品。

### HVD 命令行启停

- **现象**：不会脱离 IDE 起模拟器。
- **正确做法**：见 `dwy-arkts-ui-build.md` §12。
- **适用**：脚本化调试。
