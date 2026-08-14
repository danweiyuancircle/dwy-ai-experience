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
    'Usage:',
    '  dwy                  交互同步：选范围（完整/仅 Skills）、平台、skill 落点',
    '  dwy sync             同上',
    '  dwy skills install   强制刷新全局外部 skill 到 ~/.dwy/skills',
    '  dwy skills --help    显示 skills 子命令',
    '  dwy --help           显示本说明',
    '  dwy -h               显示本说明',
    '  dwy --version        显示当前版本',
    '  dwy -V               显示当前版本',
    '',
    'Skills:',
    '  dwy skills install   按清单安装/覆盖更新 pm-skills、superpowers（一台机一份）',
    '',
  ].join('\n')
}

/**
 * skills 子命令帮助：`dwy skills` / `dwy skills --help`。
 */
export function buildSkillsHelpText() {
  return [
    'dwy skills',
    '',
    'Usage:',
    '  dwy skills install   强制刷新全局外部 skill 到 ~/.dwy/skills',
    '  dwy skills --help    显示本说明',
    '',
  ].join('\n')
}
