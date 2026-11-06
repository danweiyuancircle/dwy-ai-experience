# dwy 配置同步

`dwy` 与 `dwy sync` 使用同一交互流程。首次安装运行 `npm install -g create-dwy@latest`，进入项目目录后运行 `dwy`；用户主目录只能选择全局范围。

## 交互顺序

1. 选择当前项目或全局范围。
2. 选择 Skills。
3. 仅项目范围选择 Rules，全局不显示此页。
4. 选择 AGENTS.md 通用规范，默认启用。
5. 选择 Hooks，默认启用。
6. 最后选择 CLI。首次只选 Codex；后续恢复当前范围同步过的 CLI 和有效旧托管入口。全局不提供 Cursor。
7. 按最终 CLI 重新核算全局覆盖，预览实际写入、迁移、备份和清理。
8. 确认后执行，完成页显示实际结果。

不再单独选择内容类型。Skills / Rules 用左右键切分类、上下键移动、Space 勾选、`a` 全选或清空当前分类；Enter 确认当前步骤，Esc 或 Ctrl+C 取消。

确认前只允许获取模板缓存。项目配置、全局配置、共享已安装 Skills 的写入、迁移、刷新和清理均在确认后执行；取消不改同步目标。

## 全局覆盖与移除

项目检测到有效全局通用规范，或全部所需 Hooks 都有有效全局注册时，完全跳过对应操作页，不重复写入。Hook 是否有效同时检查脚本、事件、matcher 和完整命令注册，不能只看文件存在。

项目 AGENTS.md 由多个 CLI 共享。任一适用 CLI 已有有效的 dwy 全局通用规范时，项目继承全局规范并清理重复基线；最终选择中缺失全局规范的 CLI 会在预览中提示，需要另行选择全局范围补齐，不借项目流程改写全局。手写 AGENTS.md 本身不代表已安装 dwy 全局规范。项目 Rules 与通用规范独立管理，移除任一托管块都保留另一个块和手写内容。

Skills 副本集中在用户目录的 `.dwy/skills`，项目和全局通过目录链接使用。主交互先选择 Skills，最后按实际 CLI 的全局覆盖去重，只为缺少全局入口的 CLI 安装项目链接；脚本提前指定平台时，选择页会禁用已被全部适用 CLI 全局覆盖的项。项目同步不借补入口刷新其他 CLI 正在使用的全局同名共享内容；可刷新共享项的预览明确说明所有同名链接会同时生效。

取消已有 Skills / Rules 勾选，或关闭通用规范 / Hooks，只移除当前范围的托管内容。项目操作不移除全局配置，也不改写有效全局提供者。全局启用时会预览当前项目重复项的清理；全局移除不会自动向项目补装。真实目录先备份到同步根的 `.dwy/skill-backups`。

## 模板与程序分别更新

模板固定来自公开仓库 [dwy-ai-experience](https://github.com/danweiyuancircle/dwy-ai-experience) 的 `master` 分支 `dwy-cli/templates/ai-tools`，缓存在用户目录的 `.dwy/template-source`。运行时检查远端 commit，未变更时复用缓存；离线保留有效缓存，无有效缓存时使用 CLI 包内模板并提示降级来源。首次获取需要网络传输整套模板，终端显示进度；实现使用 [Git 浅克隆与稀疏检出](https://git-scm.com/docs/git-clone)。开发时设置 `DWY_TEMPLATE_SOURCE_DIR` 可优先使用本地模板目录。

新增 Skills 只需更新模板分发分支，不必发布新版 CLI。模板缓存更新不会自动改写已安装的共享 Skills。

| 入口 | 用途 |
| --- | --- |
| `dwy` / `dwy sync` | 使用最新可用模板，确认后同步所选配置，并刷新本次所选、需由当前范围提供的共享 Skills |
| `dwy refresh` | 从最新可用模板刷新已安装共享 Skills，无需升级 CLI；已有链接同时生效 |
| `dwy upgrade` | 更新到 npm 最新正式版程序，并刷新共享 Skills |
| `dwy migrate` | 迁移当前项目已有托管 Skills，真实目录先备份，无需重新勾选 |

Rules / Hooks 更新仍需执行 `dwy sync`。已有会话可能缓存 Skill 内容，需要重新加载。个人 Skills、Rules、Hooks 不参与 `dwy migrate`；脚本层的 sync / migrate 接口仍须显式指定范围，不从上一次交互猜测。
