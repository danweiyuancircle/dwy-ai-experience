---
name: dwy-post-publish
description: "dwy-cli 发版后自动更新本地全局 CLI。触发条件：执行了 pnpm publish:cli 或 npm publish（在 claude-cli 目录下）后。"
---

# DWY CLI 发版后更新本地

当 `create-dwy` 成功发布到 npm 后，**必须立即执行以下步骤**更新本地全局 CLI。

## 触发条件

以下任一情况发生后，**自动执行**（不需要用户确认）：

1. 执行了 `pnpm publish:cli` 且成功
2. 执行了 `npm publish`（在 claude-cli 目录下）且成功

## 执行步骤

```bash
# 1. 等待 npm 注册表同步（通常 < 30 秒）
npm view create-dwy version

# 2. 更新全局 CLI
npm i -g create-dwy@latest

# 3. 验证版本一致
dwy --version
```

## 验证

更新后的 `dwy --version` 输出必须与刚发布的版本号一致。如果不一致，等待 30 秒后重试一次。
