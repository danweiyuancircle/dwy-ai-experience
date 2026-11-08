---
description: 只有 develop 和 preview。develop 只发 beta/rc 到测试环境，正式版只从 preview 发。仓库没按这个来要先提醒。只在部署和发版相关文件上注入。
paths:
  - "**/.github/workflows/**"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/compose.yml"
  - "**/compose.yaml"
  - "**/deploy*"
  - "**/Dockerfile"
  - "**/Dockerfile.*"
---

# 正式环境分支

只在部署、发版时遵守。日常改业务代码时忽略本文件。

只有两条长期分支，不另建 release / hotfix 分支。

- `develop`：开发，只更新测试环境。这里发出的版本只能是 `beta` 或 `rc`。还在改用 `beta`，准备进 `preview` 用 `rc`。
- `preview`：正式环境。只有这里发正式版，版本号不带 `-beta` / `-rc`。

仓库没有这两条分支，或正式环境不是从 `preview` 发：先提醒，不要自行建分支，不要把 `main` / `master` 当成 `preview`。

用 `develop` 部署正式环境，或在 `develop` 上打不带预发布的正式号：先停，按下面这段问。确认前不要做。

> 当前在 develop。develop 只更新测试环境，版本只能是 beta 或 rc。
> 正式版要到 preview 上发。
> 请确认这次是否仍要继续。

用户不确认：不要部署，不要打正式号。用户明确确认后，才可以继续这一次。
