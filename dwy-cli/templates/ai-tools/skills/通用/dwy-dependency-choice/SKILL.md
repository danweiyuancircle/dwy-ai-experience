---
name: dwy-dependency-choice
description: "新增或升级运行时依赖、选版本、选基础镜像 / SDK、检查开源许可证时必须使用（即使用户没说 skill 名）。只选发布满 7 天的正式版；闭源商用禁止 GPL / AGPL / SSPL / 非商业许可。各栈查发布时间和隐私协议附录模板在本 skill。不负责本包自己的 SemVer（那是 dwy-semver）。已安装的旧版本不用为此升级。"
---

# 依赖选型（版本 + 许可）

新装或新选依赖、base 镜像、SDK、字体、图标、素材、模型权重时读本 skill。已安装的旧版本不用为此升级。本包自己的版本号走 `dwy-semver`。

没有 skill 的工具只看这两份短 rule，和本 skill 冲突时以本 skill 为准：`rules/开发流程/dwy-dependency-freshness.md`、`rules/开发流程/dwy-oss-commercial-license.md`。

## 一、版本

预发布（beta / rc / alpha）未冻结 API。刚发布的正式版也常带回归。先丢掉预发布，再查正式版的首次发布时间，避开不满 7 天的版本。

适用所有包管理器。下面没列出的栈，查该包实际所在的 registry。

### 适用边界

- 只约束首次选型：新项目引入新包、新搭脚手架选 base 镜像 / SDK、原项目引入此前没用过的依赖。
- 已安装的旧版本无需为此升级。
- 7 天是下限排除条件，不是「必须选最近一个满 7 天的版本」。最终选哪个稳定正式版，看成熟度、维护、体积、和当前栈是否兼容。

### 硬约束

候选必须同时满足下面两条。给用户的选项同样只列合格版本。

- 只选正式版。禁止版本号或 tag 含 `beta` / `rc` / `alpha` / `preview` / `nightly` / `snapshot` / `canary` / `dev` / `experimental`，或 registry 标为 pre-release（npm dist-tag `next` / `beta` / `rc`、GitHub `prerelease: true`、PyPI 版本号带 `a` / `b` / `rc`）。预发布即使超过 7 天也不用。
- 选定前查该正式版的首次发布时间。用官方 registry 的发布时间，不是上传时间，不是 `latest` / `stable` tag 时间。
- 禁止采用发布时间距今不满 7 天的版本。含安全补丁，无例外。等满 7 天再用。
- 禁止 `@latest` / `latest` / `stable` / 浮动 tag / 不带版本号。这些会落到刚发布的版本或预发布通道。
- 用户口头点名某个 beta / rc：不直接装。说明只选正式版，改给最近一个合格正式版让用户确认。

### 各栈查发布时间

表里的 URL 和字段是当前先验。包不在这个宿主、字段不是首次发布，或请求失败，就换它实际所在的 registry 或发行说明。不要用示例版本号顶上。查到的新入口不要写回本表。

| 栈 | 查发布时间 |
| --- | --- |
| npm / pnpm | 先验：`npm view <pkg> time --json`。官方 registry 连不上，或包不在 npmjs，改查实际所在的 registry。刚发布的传播延迟不是换源的理由 |
| uv / pip | 先验：`https://pypi.org/pypi/<pkg>/json`。取该版本各文件里最早的 `upload_time`，不要默认 `[0]` 就是首次。包不在 pypi.org 就查它实际所在的 index |
| Docker | 查该 tag 的首次发布时间。Hub tags API 的 `last_updated` 会因重复推送变动，不能当成首次发布。Hub 不通或镜像不在 Hub 时改查它所在 registry |
| Android（Gradle / Maven） | 先验：包所在仓库的 `maven-metadata.xml`。`<lastUpdated>` 会随元数据重写，不能单独当成首次发布。对不上就看该版本的发行说明或 tag。包不在 Maven Central 就查它实际的仓库 |
| iOS（CocoaPods） | 先验：`https://github.com/CocoaPods/Specs` 或该 pod 源仓库的 release / tag。不在 Specs 里就查实际 spec 源 |
| iOS（SPM） | 源仓库 release / tag 时间 |
| 鸿蒙（ohpm） | 先验：ohpm registry 包元数据 publishTime。这个 host 没有该包就查项目实际使用的 ohpm 源 |
| Flutter（pub） | 先验：`https://pub.dev/packages/<pkg>` 的 published，或 pub API。私有 pub 用那个 host |

拿不到精确发布时间：选更早的正式版，不选「最新」，不选 beta。

```bash
# 反例：预发布，即使发布超过 7 天也不用
pnpm add some-pkg@1.3.0-beta.2
uv add some-pkg==2.0.0rc1
FROM node:23.0.0-rc

# 反例：直接装 latest
pnpm add some-pkg@latest
FROM node:latest

# 正例：先查正式版发布时间，再锁一个已满 7 天的正式版
npm view some-pkg time --json
pnpm add some-pkg@1.2.3
```

## 二、许可

闭源商用（收费、SaaS、付费 App、对外交付）引入开源库时查许可。纯学习原型先不挡；一旦上架或收费，补齐本节。

当前仓库本身是对外发布的开源库时，依赖许可按该库自己的许可证评估。GPL 不因为本节自动禁止。

只查直接依赖，不强制盘传递依赖。覆盖 npm/pnpm、PyPI/uv、CocoaPods/SPM、Gradle/Maven、ohpm、pub、Docker 基础镜像、字体、图标、素材、模型权重与 SDK。

### 三条

1. 未确认 license 的包禁止引入。
2. 明确不可商用或强 copyleft：换可商用替代，或购买商业授权。不要直接使用。
3. 只有许可强制要求署名 / NOTICE 时，才在隐私协议附录声明（含锁定版本）。不强制署名的库不写。

### 禁止引入

| 类型 | 常见标识 | 原因 |
| --- | --- | --- |
| 明确非商业 | `CC-BY-NC*`、`CC-NC`、`PolyForm-Noncommercial`、许可证写 Non-Commercial / No Commercial Use | 商用即侵权 |
| 强传染 copyleft（闭源商用） | `GPL-2.0`、`GPL-3.0`、`AGPL-3.0`、`SSPL` | 可能强制整包开源或限制网络服务形态 |
| 限制竞争 / 生产用途 | `BUSL`（未到 Change Date 且限制 Production）、Commons Clause、部分 Source-Available | 表面开源，实则禁商用或禁竞争 |
| 仅免费个人 / 评估 | 字体、图标、SDK 写 free for personal use only、evaluation only | 商用需买授权 |
| 无 license | 仓库无 LICENSE，或 all rights reserved 却当开源用 | 默认不可用 |

已知会把上表许可顶进运行时链接的包也不得引。

例外必须记下来：已购买商业授权且合同覆盖当前用途（授权方、合同编号、到期日）；LGPL 不得默认通过，单独评估后再定。

选型对比加一列 License：

- `OK-商用`：可商用，无强制署名则声明页可不写
- `OK-商用+强制署名`：MIT / BSD / Apache-2.0 / ISC 等要求保留版权与许可声明，进隐私协议附录
- `OK-商用+额外义务`：Apache NOTICE、MPL 文件级 copyleft，按义务处理
- `禁-不可商用/高风险`：不得作为推荐默认项

### 强制署名时的声明

许可明确要求 attribution / copyright notice / NOTICE / 保留许可文本时才声明。

落点只有隐私协议附录「第三方开源组件」。不写进个人信息处理条款正文。关于页可以链到附录，不替代附录。

| 字段 | 说明 |
| --- | --- |
| 组件名 | 直接依赖包名 |
| 版本 | lockfile 里的锁定版本，禁止只写 `latest` |
| 许可证 | SPDX 标识 |
| 版权声明 | 来自 LICENSE 或包元数据 |
| 许可全文或链接 | 全文或稳定 URL |

```text
附录：第三方开源组件

本产品直接使用的、且许可证要求保留声明的开源组件如下：

1. axios 1.7.9
   License: MIT
   Copyright (c) 2014-present Matt Zabriskie
   https://github.com/axios/axios/blob/v1.7.9/LICENSE
```

只列直接依赖里许可强制署名的项。新增、替换、锁定版本变更时更新附录。发版前附录版本与 lockfile 一致，已移除的组件从附录删掉。

### 常见许可

| SPDX | 商用闭源 | 是否强制进附录 |
| --- | --- | --- |
| MIT / ISC / BSD-2/3 | 可 | 是 |
| Apache-2.0 | 可 | 是（保留 NOTICE） |
| MPL-2.0 | 通常可 | 按义务；改过的 MPL 文件另有开源义务 |
| LGPL-2.1/3.0 | 须单独评估 | 评估通过后再定 |
| GPL / AGPL / SSPL | 禁 | — |
| CC-BY-NC* | 禁 | — |
| 无 license | 禁 | — |

推荐开源方案时带上 license 和商用结论（OK / OK+强制署名 / 禁 / 需商业授权）。禁区许可不作为默认推荐，改列可商用替代。不得以「业界都在用」跳过核查。
