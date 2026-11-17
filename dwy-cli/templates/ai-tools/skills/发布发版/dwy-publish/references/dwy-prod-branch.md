---
description: 仅适用于明确采用 develop/preview 约定的项目；约束部署环境，不按分支决定版本类型。默认正式版，预发布须由用户明确要求。
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

仅明确采用本约定的项目在部署、发版时遵守。日常改业务代码时忽略本文件。版本类型遵循 `SKILL.md`：默认正式版，只有用户明确要求时才使用预发布版本。

只有两条长期分支，不另建 release / hotfix 分支。

- `develop`：开发，只更新测试环境；不因分支自动添加 beta、rc 等预发布标识。
- `preview`：更新正式环境；版本类型由用户要求决定，不由部署环境推导。

仓库没有这两条分支，或正式环境不是从 `preview` 发：先提醒，不要自行建分支，不要把 `main` / `master` 当成 `preview`。

用 `develop` 部署正式环境：先停，按下面这段问。确认前不要部署。仅创建正式版本号或 tag 不触发此确认。

> 当前在 develop，本项目约定从 preview 部署正式环境。
> 请确认这次是否仍要从 develop 部署正式环境。

用户不确认：不要部署正式环境。用户明确确认后，才可以继续这一次。
