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
    '  dwy            选择范围、平台和处理内容，预览清单后同步',
    '  dwy sync       同上',
    '  dwy upgrade    升级到 npm 最新正式版，并刷新共享 Skills',
    '  dwy refresh    用当前 CLI 模板刷新已安装的共享 Skills',
    '  dwy migrate    一键迁移老项目已有的托管 Skills，原目录先备份',
    '  dwy --help     显示本说明',
    '  dwy --version  显示版本',
    '',
    '同步步骤：',
    '  1. 选择同步范围：当前项目或全局。',
    '  2. 选择该范围支持的平台；全局不提供 Cursor。',
    '  3. 选择本次处理内容；项目默认只选 Skills，全局首次默认 Skills 和通用规范。',
    '     项目：Skills、Hooks、Rules、AGENTS.md 通用规范；全局：Skills、Hooks、AGENTS.md 通用规范。',
    '     内容按平台能力过滤；未选择的类型保持原样。',
    '  4. 逐项选择 Skills / Rules；Hooks 和通用规范分别选择启用/更新或移除。',
    '  5. 查看写入、备份和清理清单，确认后执行；取消不写文件。',
    '  Commands 不参与同步。',
    '',
    '交互按键：',
    '  Skills / Rules：←/→ 切分类，↑/↓ 移动，Space 勾选，a 全选／清空当前分类。',
    '  范围 / 平台 / 内容：↑/↓ 移动；多选用 Space 勾选，可输入关键字筛选。',
    '  Enter 确认当前步骤，Esc 或 Ctrl+C 取消。',
    '',
    '常见用法：',
    '  同步当前项目：cd your-project 后执行 dwy，选择「当前项目」及本次处理内容。',
    '  同步全局：执行 dwy，选择「全局」及 Skills、Hooks 或 AGENTS.md 通用规范。',
    '  移除配置：选择对应范围和 Hooks / 通用规范，再选择「移除」并确认。',
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
    '同步仅处理当前范围、所选平台和内容；未选择的类型及其记录保持原样。',
    '用户主目录不能作为项目范围同步，请选择全局或进入项目目录。',
    '取消已有勾选会在确认后移除当前范围的托管入口；不勾选整个类型则不处理。',
    'Skills 副本集中在 ~/.dwy/skills；项目和全局使用目录链接，同平台全局入口优先。',
    '项目 Skills 全部适用平台均有全局入口时显示「全局已启用」，不能重复勾选。',
    '部分平台已有全局入口时仍可选，只为缺少全局入口的平台安装项目链接。',
    'Hooks 与 Skills 独立；整组管理，项目仅安装缺少有效全局注册的 Hooks。',
    '全局 Hook 的脚本与对应事件、matcher、完整命令注册均有效时，项目禁止重复安装。',
    '任一所选 CLI 已有 dwy 全局通用规范时，项目只能继承并清理重复基线；其他 CLI 需补齐全局规范。',
    '手写 AGENTS.md 本身不算全局已安装；通用规范与 Rules 共用文件但独立管理。',
    '移除通用规范仅删除基线块，保留 Rules 和手写内容；移除后不会因默认值自动重新启用。',
    '全局启用会明确列出当前项目重复项清理；全局移除不会自动向项目补装。',
    '项目同步只清理项目重复入口，不改全局提供者；真实目录先备份。',
    'sync / migrate 仅准备缺失或损坏副本，不刷新已有共享内容；refresh / upgrade 才刷新。',
    '产品流程缺失的外部依赖也列入清单，确认后联网补齐，已有内容保留。',
    '旧真实目录备份到同步根的 .dwy/skill-backups；个人 Skills、Rules、Hooks 不参与 migrate。',
    '旧项目首次需执行 dwy migrate；迁移后无需逐项目刷新 Skills。',
    'Rules / Hooks 的模板更新仍需执行 dwy sync；已有会话缓存的 Skill 可能需要重新加载。',
    '',
  ].join('\n')
}
