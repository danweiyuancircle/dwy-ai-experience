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
    '  dwy            选择 Skills / Rules，再同步到全局或项目',
    '  dwy sync       同上',
    '  dwy upgrade    把 dwy 升级到 npm 最新正式版',
    '  dwy --help     显示本说明',
    '  dwy --version  显示版本',
    '',
    '同步步骤：',
    '  1. 选择 Skills，再选择 Rules；按分类逐项勾选。',
    '  2. 选择当前项目或全局，再选择要同步的平台。',
    '  3. 查看更新、删除项，确认后才写入；取消不写文件。',
    '  Hooks 按平台自动同步，无需选择；Commands 不参与同步。',
    '',
    '交互按键：',
    '  Skills / Rules：←/→ 切分类，↑/↓ 移动，Space 勾选，a 全选／清空当前分类。',
    '  位置 / 平台：↑/↓ 移动；平台用 Space 勾选，可输入关键字筛选。',
    '  Enter 确认当前步骤，Esc 或 Ctrl+C 取消。',
    '',
    '常见用法：',
    '  同步当前项目：cd your-project 后执行 dwy，在位置步骤选择「当前项目」。',
    '  同步全局配置：任意目录执行 dwy，在位置步骤选择「全局」。',
    '  更新或调整配置：再次执行 dwy sync，检查勾选项，再确认同步。',
    '  更新 CLI：dwy upgrade（全局安装时可用；更新后执行 dwy --version 查看版本）。',
    '  首次安装：npm install -g create-dwy@latest',
    '',
    '平台支持：',
    '  Claude Code / Codex：项目或全局的 Skills、Rules、Hooks。',
    '  OpenCode：项目或全局的 Skills、Rules；当前不支持 Hooks。',
    '  Cursor：仅项目 Rules；全局规则在 Cursor 设置中管理。',
    '',
    '同步仅处理所选位置和平台；取消已勾选的托管项会在确认后删除。',
    '更新 CLI 只升级工具；本地配置需再执行 dwy sync 更新。',
    '',
  ].join('\n')
}
