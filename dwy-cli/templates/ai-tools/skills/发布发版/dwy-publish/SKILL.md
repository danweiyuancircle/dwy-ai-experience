---
name: dwy-publish
description: "发版/部署编排器。触发条件：用户说\"发版\"\"部署\"\"发布上线\"\"release\"\"publish\"\"走发版流程\"时。按应用目录确认发布方式并缓存，串起定版本→changelog→安全检查→build/发布→监控→通知。版本号决策单独走 dwy-semver，GA 打包走 dwy-github-action-publish，发布前安全检查走 dwy-sdk-spec——本 skill 负责编排，按路径主动调它们。"
---

# 发版编排器

一条发版链的编排执行。进入前测试已完成。

**先**读仓库上下文，判目标平台（前端/后端/Android/iOS/鸿蒙/通用）+ 定位应用目录（相对项目根的相对路径）。**再**按下表执行 8 步。

| # | 步骤 | 类型 | 调用 |
|---|------|------|------|
| 1 | 确认发布方式 + 探测 build/publish 命令 | 项目步 | `scripts/release_config.sh` + `references/publish-config.md` |
| 2 | 写/校验发布配置（GA workflow / TestFlight 就绪） | 项目步 | `references/publish-config.md` |
| 3 | 定版本号 + 多文件同步 | 通用步 | `../dwy-semver` + `references/version-sync.md` |
| 4 | 写 changelog（按平台子目录） | 通用步 | `references/changelog.md` |
| 5 | 安全检查（闸门，未过不发） | 通用步 | `../dwy-sdk-spec` |
| 6 | build + 触发发布 | 项目步 | `references/<平台>.md`；走 GA 引 `../dwy-github-action-publish` |
| 7 | 监控发布进程 | 项目步 | `references/monitor-notify.md` |
| 8 | 通知结果（输出结果文本） | — | `references/monitor-notify.md` |

平台流程文件：`frontend-deploy.md` / `backend-deploy.md` / `ios.md` / `android.md` / `harmony.md` / `generic-release.md`。

## 编排约束

- **通用步固化**（定版本/changelog/安全检查跨项目一致，走子 skill/脚本）；**项目步读上下文+缓存**（build/deploy/监控命令因项目而异，**绝不写死**，探测不到问用户后缓存）。
- 安全检查（第 5 步）是闸门，未过不进发布。
- 全程 AI 自动判断、自动跑，仅搞不定时才问用户（版本级别拿不准、命令探测不到、配置缺失、构建/发布失败）。
- 编排时按文件路径主动加载子 skill（`../dwy-semver`、`../dwy-sdk-spec`、`../dwy-github-action-publish`）；这些 skill 也可被用户独立触发。
- `.dwy/` 缓存提醒用户加进 `.gitignore`。
