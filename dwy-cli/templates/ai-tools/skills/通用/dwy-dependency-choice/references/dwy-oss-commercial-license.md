---
description: 闭源商用新装依赖的许可硬约束。声明模板和许可表见 skill dwy-dependency-choice。只在改依赖清单时注入。开源库仓库按该库自身许可证评估。
paths:
  - "**/package.json"
  - "**/pnpm-lock.yaml"
  - "**/yarn.lock"
  - "**/package-lock.json"
  - "**/pyproject.toml"
  - "**/uv.lock"
  - "**/requirements*.txt"
  - "**/Podfile"
  - "**/Package.swift"
  - "**/Package.resolved"
  - "**/build.gradle"
  - "**/build.gradle.kts"
  - "**/libs.versions.toml"
  - "**/oh-package.json5"
  - "**/pubspec.yaml"
  - "**/go.mod"
  - "**/Cargo.toml"
  - "**/Dockerfile"
  - "**/Dockerfile.*"
---

# 商用依赖许可（硬约束）

闭源商用产品新装直接依赖时遵守。学习原型在上架或收费前补齐。当前仓库本身是对外开源库时，按该库自己的许可证评估，GPL 不因此自动禁止。附录模板和许可表见 skill `dwy-dependency-choice`。和本文件冲突时以该 skill 为准。

- 先查许可证再装。无 LICENSE，或 all rights reserved 却当开源用：禁止。
- 禁止直接依赖：`CC-BY-NC*`、`PolyForm-Noncommercial`、`GPL-2.0`、`GPL-3.0`、`AGPL-3.0`、`SSPL`、未到期且限制生产的 `BUSL`、Commons Clause、仅个人或评估可用的字体 / 图标 / SDK。
- LGPL 和已购商业授权不默认通过，单独记一笔再定。
- 只有许可证强制署名或 NOTICE 的直接依赖才写入隐私协议附录，并写 lockfile 里的版本。不强制署名的不写。
