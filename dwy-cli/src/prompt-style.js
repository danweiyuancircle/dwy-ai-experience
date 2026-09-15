/**
 * CLI 列表行聚焦样式。
 * 只靠 dim 在 JetBrains / 部分终端看不出光标；已勾选时勾选框又全是绿块。
 * 指针字符不依赖颜色，反底在支持 ANSI 的终端再加强。
 */

import { styleText } from 'node:util'
import process from 'node:process'

/** 是否支持 unicode 符号（与 clack prompts 判定一致） */
function isUnicodeSupported() {
  if (process.platform !== 'win32') {
    return process.env.TERM !== 'linux'
  }
  return Boolean(process.env.CI)
    || Boolean(process.env.WT_SESSION)
    || Boolean(process.env.TERMINUS_SUBLIME)
    || process.env.ConEmuTask === '{cmd::Cmder}'
    || process.env.TERM_PROGRAM === 'Terminus-Sublime'
    || process.env.TERM_PROGRAM === 'vscode'
    || process.env.TERM === 'xterm-256color'
    || process.env.TERM === 'alacritty'
    || process.env.TERMINAL_EMULATOR === 'JetBrains-JediTerm'
}

const unicode = isUnicodeSupported()
const unicodeOr = (c, fallback) => (unicode ? c : fallback)

/** 光标指针。无 unicode 时用 ASCII，保证去 ANSI 后仍能看出聚焦行。 */
const S_POINTER = unicodeOr('›', '>')
const S_RADIO_ACTIVE = unicodeOr('●', '>')
const S_RADIO_INACTIVE = unicodeOr('○', ' ')
const S_CHECKBOX_ACTIVE = unicodeOr('◻', '[•]')
const S_CHECKBOX_SELECTED = unicodeOr('◼', '[+]')
const S_CHECKBOX_INACTIVE = unicodeOr('◻', '[ ]')

/**
 * 聚焦文案：反底芯片。无色终端退回原文字，靠指针区分。
 *
 * @param {string} label
 * @param {boolean} active
 */
function formatLabel(label, active) {
  if (active) return styleText(['bgCyan', 'black'], ` ${label} `)
  return styleText('dim', label)
}

/**
 * 多选一行。
 * selected=已勾；active=当前光标。disabled 时不响应聚焦样式。
 *
 * @param {{ label: string, selected?: boolean, active?: boolean, prefix?: string, disabled?: boolean }} opts
 */
export function formatCheckboxRow({ label, selected = false, active = false, prefix = '', disabled = false }) {
  const prefixPart = prefix ? `${prefix} ` : ''
  if (disabled) {
    return `  ${styleText('dim', S_CHECKBOX_INACTIVE)} ${prefixPart}${styleText(['strikethrough', 'dim'], label)}`
  }
  const pointer = active ? styleText('cyan', S_POINTER) : ' '
  const box = selected
    ? styleText('green', S_CHECKBOX_SELECTED)
    : active
      ? styleText('cyan', S_CHECKBOX_ACTIVE)
      : styleText('dim', S_CHECKBOX_INACTIVE)
  return `${pointer} ${box} ${prefixPart}${formatLabel(label, active)}`
}

/**
 * 单选一行。disabled 画删除线，不画指针。
 *
 * @param {{ label: string, active?: boolean, disabled?: boolean }} opts
 */
export function formatRadioRow({ label, active = false, disabled = false }) {
  if (disabled) {
    return `  ${styleText('gray', S_RADIO_INACTIVE)} ${styleText(['strikethrough', 'gray'], label)}`
  }
  const pointer = active ? styleText('cyan', S_POINTER) : ' '
  const radio = active
    ? styleText('green', S_RADIO_ACTIVE)
    : styleText('dim', S_RADIO_INACTIVE)
  return `${pointer} ${radio} ${formatLabel(label, active)}`
}
