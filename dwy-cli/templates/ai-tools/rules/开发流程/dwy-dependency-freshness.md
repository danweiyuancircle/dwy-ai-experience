---
description: 依赖版本选择通用规则（首次技术选型只选正式版、禁止 beta/rc 等预发布；发布 <7 天的版本不采用；跨 npm/uv/Docker/Android/iOS/鸿蒙/Flutter 等所有栈）
---

# 依赖版本新鲜度规则

> 首次技术选型下载依赖（引新包、选 base 镜像 / SDK 版本）时，预发布版（beta / rc / alpha）未冻结 API，刚发布的正式版也常带回归 bug。本规则约束 AI 在装新依赖前：先丢掉预发布，再查正式版「首次发布时间」，避开 <7 天的版本。
>
> 适用**所有技术栈**：npm/pnpm、uv/pip、Docker、Android(Gradle/Maven)、iOS(CocoaPods/SPM)、鸿蒙(ohpm)、Flutter(pub) 以及未来出现的任何包管理器。下面给出总约束 + 各栈示例，未列出的栈按「查官方 registry 发布时间」通用流程自行判断。

## 一、适用边界

- **仅约束首次技术选型下载依赖**：新项目引入新包、新搭脚手架选 base 镜像 / SDK 版本、原项目引入此前没用过的依赖。
- **已安装的旧版本无需为此升级**。本规则只管「新装 / 新选」，不管「存量升级」。
- 7 天是**下限排除条件**，不是「必须选最近一个 ≥7 天的版本」。最终选哪个稳定正式版由 AI 综合判断（成熟度、维护活跃度、依赖体积、与项目栈兼容性）。

## 二、核心约束

候选版本必须**同时**满足下面两条，缺一不可。给用户的 AskUserQuestion 选项同样只列合格版本，禁止把预发布号摆上去让用户选。

- **必须只选正式版**
  - **禁止**采用预发布：版本号或 tag 含 `beta` / `rc` / `alpha` / `preview` / `nightly` / `snapshot` / `canary` / `dev` / `experimental`，或 registry 标为 pre-release（npm dist-tag `next`/`beta`/`rc`、GitHub `prerelease: true`、PyPI 版本号带 `a`/`b`/`rc`）
  - 先滤掉预发布，再进入 7 天判断；预发布即使发布超过 7 天也不用
- **必须**在首次安装 / 选定版本前，查候选**正式版**的「首次发布时间」
  - 用官方 registry 的发布时间，**不是**上传时间、**不是** `latest` / `stable` tag 时间
- **禁止**采用发布时间距今 **<7 天**的版本
- **禁止**无脑用 `@latest` / `latest` / `stable` / 浮动 tag / 不带版本号安装——这些随时可能落到刚发布的新版本或预发布通道上
- 已安装版本**无需**为此规则升级

## 三、各栈查发布时间示例

未列出的栈，按「查官方 registry 元数据 → 取发布时间」自行处理。查的对象必须是正式版，预发布条目直接跳过。

| 栈 | 查发布时间方法 |
|---|---|
| npm / pnpm | `npm view <pkg> time --json`（取目标版本对应的时间字段） |
| uv / pip | PyPI JSON API：`https://pypi.org/pypi/<pkg>/json` 的 `releases[<version>][0].upload_time` |
| Docker | Docker Hub 镜像页 / API 的 `last_updated`；优先看具体 tag 的 push 时间 |
| Android (Gradle/Maven) | Maven Central `maven-metadata.xml` 的 `<lastUpdated>`（格式 yyyyMMddHHmmss） |
| iOS (CocoaPods) | `https://github.com/CocoaPods/Specs` 或仓库 release / tag 时间 |
| iOS (SPM) | 源仓库 release / tag 时间 |
| 鸿蒙 (ohpm) | ohpm registry 包元数据 publishTime |
| Flutter (pub) | `https://pub.dev/packages/<pkg>/versions` 页 published 时间 |

## 四、正反例

```bash
# 反例：预发布，即使发布超过 7 天也不用
pnpm add some-pkg@1.3.0-beta.2
uv add some-pkg==2.0.0rc1
FROM node:23.0.0-rc
implementation 'com.example:lib:1.0.0-alpha'

# 反例：直接装 latest，可能落到昨天才发的正式版或预发布通道
pnpm add some-pkg@latest
uv add some-pkg          # 不锁版本
FROM node:latest         # 随时被新镜像覆盖
implementation 'com.example:lib:latest'

# 正例：正式版，且发布 ≥7 天
npm view some-pkg time --json      # 看候选正式版发布时间
pnpm add some-pkg@1.2.3            # 1.2.3 是正式版，发布已满 7 天
FROM node:20.18.1-slim             # 该 tag 是正式版，push 已满 7 天
```

## 五、AI 自判提示

- 栈未列全时，先找该栈的**官方 registry**（包管理器背后的中央仓库），丢掉预发布条目，再查正式版发布时间字段。
- 拿不到精确发布时间时，保守处理：选发布更早、更稳定的正式版，不要选「最新」，更不要选 beta。
- 7 天窗口内的新正式版，**等待**而非采用，**无任何例外**（含安全补丁）。等满 7 天再用。
- 用户口头点名某个 beta / rc：**不要直接装**。说明本规则只选正式版，改给最近一个合格正式版让用户确认。
