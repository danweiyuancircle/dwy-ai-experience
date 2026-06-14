---
name: dwy-publish
description: "部署应用、发布版本、发布 SDK 的通用发版入口。触发条件：用户说“部署”“发版”“发布”“release”“publish”“bump version”时。先根据仓库上下文判断目标是应用部署还是 SDK 发版，再分别读取对应流程文件执行。"
---

# 发布入口

通用发布 skill。默认进入本 skill 前，测试已经完成。

## 第 0 步：读取仓库发布上下文

执行前先从仓库里定位发布相关信息。

优先查看这些信息源：

- `package.json`、`pyproject.toml`、`Cargo.toml`、`Makefile`、发布脚本
- `.github/workflows/`、CI 配置、Docker 构建文件
- `README.md`、发布文档、变更日志
- 现有 tag 格式、历史 release commit、历史 workflow 运行方式

如果仍然无法判断发布方式或版本来源，停止并要求用户明确，不猜命令。

## 第 1 步：先判断发布类型

先确认：

1. 发布哪个应用或包
2. 目标是应用部署还是 SDK 发版
3. 目标版本号是什么；如果用户没给，判断是 `major` / `minor` / `patch`

归类规则：

- **应用部署**：目标是某个服务、站点、容器、镜像、二进制或线上环境
- **SDK 发版**：目标是 npm、PyPI、私有包仓库或对外库版本

多包场景按仓库已有依赖关系、workspace 拓扑、历史发布顺序执行，不自定顺序。

## 第 2 步：读取对应流程文件

- **应用部署**：读取 `references/application-release.md`
- **SDK 发版**：读取 `references/sdk-release.md`

不要把两条流程混在一起执行。先判类型，再只读对应流程文件。

## 通用约束

- 禁止在未读清仓库发布上下文时猜发布命令
- 禁止测试未完成就进入本发布流程
- 禁止构建失败后继续发布
- 禁止发布失败后对当前状态含糊表述
