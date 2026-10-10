---
description: 新装依赖只选发布满 7 天的正式版。查各栈发布时间和命令见 skill dwy-dependency-choice。只在改依赖清单时注入。
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

# 依赖版本（硬约束）

只在新装或新选依赖、base 镜像、SDK 时遵守。已安装的旧版本不用为此升级。各栈怎么查发布时间见 skill `dwy-dependency-choice`。和本文件冲突时以该 skill 为准。

- 只选正式版。禁止 `beta` / `rc` / `alpha` / `preview` / `nightly` / `snapshot` / `canary` / `dev` / `experimental`，以及 registry 标成 pre-release 的号。预发布超过 7 天也不用。
- 正式版的首次发布须满 7 天，含安全补丁。7 天是排除线，不是必须选刚满 7 天的那个。
- 禁止 `@latest` / `latest` / `stable` / 浮动 tag / 不锁版本。
- 用户点名 beta 或 rc：不直接装，改给最近一个合格正式版确认。
