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
    '  dwy            同步项目配置，或刷新全局外部 skill',
    '  dwy sync       同上',
    '  dwy upgrade    把 dwy 升级到 npm 最新正式版',
    '  dwy --help     显示本说明',
    '  dwy --version  显示版本',
    '',
  ].join('\n')
}
