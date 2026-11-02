/**
 * dwy 命令行帮助文案。
 * 已实现的入口必须出现在这里；禁止把可用命令藏进「隐藏」段。
 */

/**
 * 主帮助：`dwy --help`。
 * version 来自 package.json，调用方传入，避免本模块读盘。
 *
 * @param {string} version
 */
export function buildHelpText(version) {
  return [
    `dwy ${version}`,
    '',
    '用法：',
    '  dwy            全局更新通用基线，项目注入所选 Rules；Skills / Hooks 可选位置',
    '  dwy sync       同上',
    '  dwy upgrade    升级到 npm 最新正式版，并刷新共享 Skills',
    '  dwy refresh    用当前 CLI 模板刷新已安装的共享 Skills',
    '  dwy migrate    一键迁移老项目已有的托管 Skills，原目录先备份',
    '  dwy --help     显示本说明',
    '  dwy --version  显示版本',
    '',
    '同步步骤：',
    '  1. 选择 Skills，再选择 Rules；按分类逐项勾选。',
    '  2. 选择 Skills / Hooks 写入当前项目或全局，再选择平台。',
    '  3. 查看更新、删除项，确认后才写入；取消不写文件。',
    '  通用基线默认写入所选 CLI 的全局入口；所选 Rules 写入项目根 AGENTS.md。',
    '  Hooks 按平台自动同步，无需选择；Commands 不参与同步。',
    '',
    '交互按键：',
    '  Skills / Rules：←/→ 切分类，↑/↓ 移动，Space 勾选，a 全选／清空当前分类。',
    '  位置 / 平台：↑/↓ 移动；平台用 Space 勾选，可输入关键字筛选。',
    '  Enter 确认当前步骤，Esc 或 Ctrl+C 取消。',
    '',
    '常见用法：',
    '  同步当前项目：cd your-project 后执行 dwy，在位置步骤选择「当前项目」。',
    '  同步全局 Skills / Hooks：在项目目录执行 dwy，在位置步骤选择「全局」。',
    '  更新或调整配置：再次执行 dwy sync，检查勾选项，再确认同步。',
    '  更新 CLI：dwy upgrade（全局安装时可用；更新后执行 dwy --version 查看版本）。',
    '  迁移老项目：cd your-project 后执行 dwy migrate，无需重新勾选。',
    '  手动升级包后：执行一次 dwy refresh，所有已迁移的链接同时生效。',
    '  首次安装：npm install -g create-dwy@latest',
    '',
    '平台支持：',
    '  Claude Code：全局 ~/.claude/CLAUDE.md；项目 Rules 使用根 AGENTS.md。',
    '  Codex：全局 $CODEX_HOME/AGENTS.md（默认 ~/.codex/AGENTS.md）；项目根 AGENTS.md。',
    '  OpenCode：全局 ~/.config/opencode/AGENTS.md；项目根 AGENTS.md；当前不支持 Hooks。',
    '  Cursor：仅项目 Rules；全局规则在 Cursor 设置中管理。',
    '',
    '同步仅处理所选平台；基线固定全局、Rules 固定项目，位置选择只影响 Skills / Hooks。',
    '取消已勾选的托管项会在确认后删除，保留手写内容。',
    'Skills 副本集中在 ~/.dwy/skills；项目和全局使用目录链接，同平台全局入口优先。',
    '旧真实目录备份到同步根的 .dwy/skill-backups；个人 Skills、Rules、Hooks 不参与 migrate。',
    '旧项目首次需执行 dwy migrate；迁移后无需逐项目刷新 Skills。',
    'Rules / Hooks 的模板更新仍需执行 dwy sync；已有会话缓存的 Skill 可能需要重新加载。',
    '',
  ].join('\n')
}
