# EUI 接入

先按 [版本与源码定位](../version-resolution.md) 从消费应用定位实际 `@dwydev/eui`，核对锁文件、解析目录、版本、exports 与类型。包未导出 `./package.json`，不能用 `require('@dwydev/eui/package.json')` 探测版本；直接读实际目录的清单。

## 选择适用资料

读同目录 `versions.yml`：1.x 对应 `v1/`，2.x 对应 `v2/`。目录不存在时查项目实际接口与对应版本资料，不能套用其他版本线。共享目录是常用约定，具体接口仍受版本约束。

| 资料 | 何时读 |
| --- | --- |
| [表单](shared/form.md) | EForm、校验与有版本下限的表单对话框 |
| [弹层](shared/overlay.md) | Dialog、Sheet 与展示状态 |
| [Reka 绑定](shared/reka.md) | primitives 的 model 绑定 |
| [配置与主题](shared/config-theme.md) | EConfigProvider、主题与本地化 |
| [2.x 导航](v2/index.md) | 组件与 composables |
| [2.x 查找](v2/lookup.md) | manifest 和声明文件 |
| [2.x 迁移](v2/breaking.md) | 删除或变更的组件 |
| [1.x 导航](v1/index.md) | 旧版本及无 manifest 时的查找 |
| [接入指南](eui-integration-guide.md) | 根 Provider、样式和项目装配 |
| [后台设计](eui-design-guide.md) | 中后台界面 |
| [落地页设计](eui-landing-design-guide.md) | 落地页 |

`component-manifest.json` ≥2.1.0、`useEuiMobile` ≥2.4；版本下限不满足时视为不可用。无 manifest 时从实际 exports/types 查找，不仅凭文件缺失判断版本。

## 源码与接入

先查实际包声明、运行产物及现有调用。slots 等信息不足时，再查对应来源的源码；发布包可补查 `@dwydev/eui@<实际版本>` tag 的 `frontend/eui/src/`，Git/workspace/patch 则核对真实提交、修改和构建产物，不优先 clone 同版本 tag。

核对根 EConfigProvider、locale、样式、peer 依赖及主题，准确确认 props、emits、slots 和生命周期。文档与实际代码冲突时以真实依赖为准；未安装或资料不足时报告缺口，不猜 props 或自动升级。共享设计资料中的示例也须按项目实际 API 调整。
