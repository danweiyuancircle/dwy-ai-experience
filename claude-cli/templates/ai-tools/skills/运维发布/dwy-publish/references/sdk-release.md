# SDK 发版流程

适用：发布目标是 npm、PyPI、私有包仓库或对外库版本。

## 主流程

流程骨架：

1. `bump`
2. `CHANGELOG`
3. `build`
4. `publish package`
5. `verify registry`

## 1. 判断是否需要 bump

SDK 发版默认需要判断版本升级。

- **需要 bump**：正式发布新版本、预发布版本、修复发布产物并重发
- **拿不准**：调用 `dwy-semver` 决定升级位和新版本号

执行顺序：

1. 读取当前版本
2. 算出新版本号
3. 修改版本文件

不要用会自动 commit 的版本命令。直接编辑版本文件。

## 2. 写 CHANGELOG

SDK 发版必须写 `CHANGELOG`。

处理顺序：

1. 找上一个 release tag
2. 查看 `git log <last-tag>..HEAD --oneline`
3. 按 `feat` / `fix` / `refactor` / `chore` 分组
4. 写入 `CHANGELOG.md` 或项目指定的 release notes 文件

如果仓库已有自动生成命令，优先使用；没有再手写。

`CHANGELOG` 未完成，不继续。

## 3. 确认测试已完成并执行 build

本流程不重复跑测试，只确认当前变更已经过项目要求的测试。

然后执行 build，确保包产物可生成。

构建失败则停止。

## 4. 决定 publish 入口

根据仓库上下文判断：

- **CI 发布**：workflow、release job、tag push、workflow_dispatch、release please、cibuildwheel
- **本地发布**：`pnpm publish`、`uv publish`、`twine upload` 或其他本地发包命令

## 5. 执行 publish package

如果是 CI 驱动：

1. 提交 release 相关文件
2. 按项目规则创建 tag；如果不是 tag 触发，则按配置触发 workflow
3. 推送分支和 tag
4. 观察发布运行状态直到成功或失败

如果是本地驱动：

1. 提交 release 相关文件
2. 按项目规则创建 tag
3. 推送分支和 tag
4. 执行本地发包命令

失败则停止，并给出失败阶段和关键报错。

## 6. verify registry

发布完成后，确认目标仓库中的新版本已可见。验证方式包括：

- npm：`npm view <pkg> version`
- PyPI：`pip index versions <pkg>` 或项目定义的检查命令
- 私有仓库：项目约定的版本查询方式
- GitHub Release：确认 release/tag 已生成

验证失败，发版不算完成。

## 禁止事项

- 禁止跳过版本升级判断
- 禁止先发包后补 `CHANGELOG`
- 禁止把包仓库验证替换成环境健康检查
