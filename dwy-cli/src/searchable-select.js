/**
 * 可搜索选择器：列表不展示 hint，底部固定「说明」公共区展示当前聚焦项描述。
 *
 * 基于 @clack/core AutocompletePrompt 自定义 render，绕过 prompts 默认「hint 跟在聚焦行后」行为。
 */

import { AutocompletePrompt, getColumns, settings } from '@clack/core'
import { limitOptions } from '@clack/prompts'
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

const S_STEP_ACTIVE = unicodeOr('◆', '*')
const S_STEP_CANCEL = unicodeOr('■', 'x')
const S_STEP_ERROR = unicodeOr('▲', 'x')
const S_STEP_SUBMIT = unicodeOr('◇', 'o')
const S_BAR = unicodeOr('│', '|')
const S_BAR_END = unicodeOr('└', '—')
const S_RADIO_ACTIVE = unicodeOr('●', '>')
const S_RADIO_INACTIVE = unicodeOr('○', ' ')
const S_CHECKBOX_SELECTED = unicodeOr('◼', '[+]')
const S_CHECKBOX_INACTIVE = unicodeOr('◻', '[ ]')

/** 底部说明区固定行数，避免列表高度随描述长短跳动 */
const DESC_PANEL_LINES = 3

/** 搜索框默认 placeholder */
export const SEARCH_PLACEHOLDER = '输入关键字筛选…'

/**
 * 按状态返回步骤符号。
 * @param {string} state
 */
function symbol(state) {
  switch (state) {
    case 'cancel':
      return styleText('red', S_STEP_CANCEL)
    case 'error':
      return styleText('yellow', S_STEP_ERROR)
    case 'submit':
      return styleText('green', S_STEP_SUBMIT)
    default:
      return styleText('cyan', S_STEP_ACTIVE)
  }
}

/**
 * 默认过滤：匹配 label / value / description。
 * @param {string} search
 * @param {{ value: unknown, label?: string, description?: string, hint?: string }} opt
 */
function defaultFilter(search, opt) {
  if (!search) return true
  const q = search.toLowerCase()
  const label = (opt.label ?? String(opt.value ?? '')).toLowerCase()
  const desc = (opt.description ?? opt.hint ?? '').toLowerCase()
  const value = String(opt.value ?? '').toLowerCase()
  return label.includes(q) || desc.includes(q) || value.includes(q)
}

/**
 * 取选项展示文案。
 * @param {{ label?: string, value?: unknown }} opt
 */
function optionLabel(opt) {
  return opt.label ?? String(opt.value ?? '')
}

/**
 * 按终端宽度硬换行（中日文按字符计，足够 CLI 展示）。
 * @param {string} text
 * @param {number} width
 * @returns {string[]}
 */
function wrapHard(text, width) {
  if (!text) return []
  const w = Math.max(width, 8)
  const lines = []
  let row = ''
  for (const ch of text) {
    if (ch === '\n') {
      lines.push(row)
      row = ''
      continue
    }
    if (row.length >= w) {
      lines.push(row)
      row = ch
    } else {
      row += ch
    }
  }
  if (row) lines.push(row)
  return lines
}

/**
 * 构建底部固定高度说明区。
 * 无描述时用占位，保证行数恒定。
 *
 * @param {string | undefined} description 当前聚焦项完整描述
 * @param {string} barPrefix 左侧竖线前缀（含颜色）
 * @param {number} contentWidth 可写字符宽
 * @returns {string[]}
 */
function buildDescPanel(description, barPrefix, contentWidth, lineCount = DESC_PANEL_LINES) {
  const raw = (description && description.trim()) ? description.trim() : '（无说明）'
  const wrapped = wrapHard(raw, contentWidth)
  const lines = []
  for (let i = 0; i < lineCount; i++) {
    let part = wrapped[i] ?? ''
    if (i === lineCount - 1 && wrapped.length > lineCount) {
      const ellipsis = '…'
      part = (wrapped[i] ?? '').slice(0, Math.max(contentWidth - ellipsis.length, 0)) + ellipsis
    }
    if (i === 0) {
      lines.push(`${barPrefix}${styleText('dim', '说明：')}${styleText('dim', part)}`)
    } else {
      // 续行缩进对齐「说明：」四字宽
      lines.push(`${barPrefix}${styleText('dim', '      ')}${styleText('dim', part)}`)
    }
  }
  return lines
}

/**
 * 从 options 中取 focusedValue 对应项的 description。
 * @param {Array<{ value: unknown, description?: string, hint?: string }>} options
 * @param {unknown} focusedValue
 */
function resolveDescription(options, focusedValue) {
  if (focusedValue === undefined) return undefined
  const hit = options.find(o => o.value === focusedValue)
  return hit?.description ?? hit?.hint
}

/**
 * 可搜索多选：列表无行内 hint，底部公共区展示当前项说明。
 *
 * @param {object} opts
 * @param {string} opts.message
 * @param {Array<{ value: unknown, label?: string, description?: string, disabled?: boolean }>} opts.options
 * @param {unknown[]} [opts.initialValues]
 * @param {boolean} [opts.required]
 * @param {number} [opts.maxItems]
 * @param {number} [opts.descLines] 底部说明区行数，包内子条目列表可加高
 * @param {string} [opts.placeholder]
 * @param {(search: string, opt: object) => boolean} [opts.filter]
 * @returns {Promise<unknown[] | symbol>}
 */
export function searchableMultiselect(opts) {
  const withGuide = opts.withGuide ?? settings.withGuide
  const placeholder = opts.placeholder ?? SEARCH_PLACEHOLDER
  const filter = opts.filter ?? defaultFilter

  const prompt = new AutocompletePrompt({
    options: opts.options,
    multiple: true,
    placeholder,
    filter,
    initialValue: opts.initialValues,
    signal: opts.signal,
    input: opts.input,
    output: opts.output,
    validate: () => {
      if (opts.required && prompt.selectedValues.length === 0) {
        return '请至少选择一项'
      }
    },
    render() {
      const msgLine = `${withGuide ? `${styleText('gray', S_BAR)}\n` : ''}${symbol(this.state)}  ${opts.message}\n`
      const userInput = this.userInput
      const isPlaceholder = userInput === '' && placeholder !== undefined
      const searchDisplay = this.isNavigating || isPlaceholder
        ? styleText('dim', isPlaceholder ? placeholder : userInput)
        : this.userInputWithCursor
      const matchHint = this.filteredOptions.length !== this.options.length
        ? styleText('dim', ` (${this.filteredOptions.length} match${this.filteredOptions.length === 1 ? '' : 'es'})`)
        : ''

      if (this.state === 'submit') {
        return `${msgLine}${withGuide ? `${styleText('gray', S_BAR)}  ` : ''}${styleText(
          'dim',
          `已选 ${this.selectedValues.length} 项`,
        )}`
      }
      if (this.state === 'cancel') {
        return `${msgLine}${withGuide ? `${styleText('gray', S_BAR)}  ` : ''}${styleText(
          ['strikethrough', 'dim'],
          userInput,
        )}`
      }

      const barColor = this.state === 'error' ? 'yellow' : 'cyan'
      const bar = withGuide ? `${styleText(barColor, S_BAR)}  ` : ''
      const barEnd = withGuide ? styleText(barColor, S_BAR_END) : ''
      const noMatch = this.filteredOptions.length === 0 && userInput
        ? [`${bar}${styleText('yellow', '无匹配项')}`]
        : []
      const errLines = this.state === 'error'
        ? [`${bar}${styleText('yellow', this.error)}`]
        : []

      const header = [
        ...`${msgLine}${withGuide ? styleText(barColor, S_BAR) : ''}`.split('\n'),
        `${bar}${styleText('dim', 'Search:')} ${searchDisplay}${matchHint}`,
        ...noMatch,
        ...errLines,
      ]

      // 底部：说明区 + 快捷键（说明区行数固定，计入 rowPadding）
      const cols = getColumns(opts.output ?? process.stdout)
      const contentWidth = Math.max(cols - (withGuide ? 10 : 6), 20)
      const descPanel = buildDescPanel(
        resolveDescription(this.filteredOptions, this.focusedValue),
        bar,
        contentWidth,
        opts.descLines ?? DESC_PANEL_LINES,
      )
      const instructions = [
        `${styleText('dim', '↑/↓')} to navigate`,
        `${styleText('dim', this.isNavigating ? 'Space/Tab:' : 'Tab:')} select`,
        `${styleText('dim', 'Enter:')} confirm`,
        `${styleText('dim', 'Type:')} to search`,
      ]
      const footer = [
        `${bar}${styleText('dim', S_BAR_H())}`,
        ...descPanel,
        `${bar}${instructions.join(' · ')}`,
        barEnd,
      ].filter(Boolean)

      const listLines = this.filteredOptions.length === 0
        ? []
        : limitOptions({
          cursor: this.cursor,
          options: this.filteredOptions,
          maxItems: opts.maxItems,
          output: opts.output,
          rowPadding: header.length + footer.length,
          style: (opt, active) => {
            const selected = this.selectedValues.includes(opt.value)
            const label = optionLabel(opt)
            const box = selected
              ? styleText('green', S_CHECKBOX_SELECTED)
              : styleText('dim', S_CHECKBOX_INACTIVE)
            if (opt.disabled) {
              return `${styleText('dim', S_CHECKBOX_INACTIVE)} ${styleText(['strikethrough', 'dim'], label)}`
            }
            // 聚焦也不拼 hint，描述只在底部公共区
            if (active) {
              return `${box} ${label}`
            }
            return `${box} ${styleText('dim', label)}`
          },
        })

      return [
        ...header,
        ...listLines.map(line => `${bar}${line}`),
        ...footer,
      ].join('\n')
    },
  })

  return prompt.prompt()
}

/** 横线字符（与 clack 一致） */
function S_BAR_H() {
  return unicodeOr('─', '-')
}

/**
 * 可搜索单选：列表无行内 hint，底部公共区展示当前项说明。
 *
 * @param {object} opts
 * @param {string} opts.message
 * @param {Array<{ value: unknown, label?: string, description?: string, disabled?: boolean }>} opts.options
 * @param {unknown} [opts.initialValue]
 * @param {number} [opts.maxItems]
 * @param {string} [opts.placeholder]
 * @param {(search: string, opt: object) => boolean} [opts.filter]
 * @returns {Promise<unknown | symbol>}
 */
export function searchableSelect(opts) {
  const withGuide = opts.withGuide ?? settings.withGuide
  const placeholder = opts.placeholder ?? SEARCH_PLACEHOLDER
  const filter = opts.filter ?? defaultFilter

  const prompt = new AutocompletePrompt({
    options: opts.options,
    multiple: false,
    placeholder,
    filter,
    initialValue: opts.initialValue !== undefined ? [opts.initialValue] : undefined,
    signal: opts.signal,
    input: opts.input,
    output: opts.output,
    validate: opts.validate,
    render() {
      const headerBase = withGuide
        ? [`${styleText('gray', S_BAR)}`, `${symbol(this.state)}  ${opts.message}`]
        : [`${symbol(this.state)}  ${opts.message}`]
      const userInput = this.userInput
      const isPlaceholder = userInput === '' && placeholder !== undefined
      let searchDisplay = ''
      if (this.isNavigating || isPlaceholder) {
        const d = isPlaceholder ? placeholder : userInput
        searchDisplay = d !== '' ? ` ${styleText('dim', d)}` : ''
      } else {
        searchDisplay = ` ${this.userInputWithCursor}`
      }
      const matchHint = this.filteredOptions.length !== this.options.length
        ? styleText(
          'dim',
          ` (${this.filteredOptions.length} match${this.filteredOptions.length === 1 ? '' : 'es'})`,
        )
        : ''

      if (this.state === 'submit') {
        const selected = this.filteredOptions.find(o => o.value === this.focusedValue)
          ?? opts.options.find(o => o.value === this.focusedValue)
        const text = selected ? optionLabel(selected) : ''
        const body = text ? `  ${styleText('dim', text)}` : ''
        const bar = withGuide ? styleText('gray', S_BAR) : ''
        return `${headerBase.join('\n')}\n${bar}${body}`
      }
      if (this.state === 'cancel') {
        const body = userInput ? `  ${styleText(['strikethrough', 'dim'], userInput)}` : ''
        const bar = withGuide ? styleText('gray', S_BAR) : ''
        return `${headerBase.join('\n')}\n${bar}${body}`
      }

      const barColor = this.state === 'error' ? 'yellow' : 'cyan'
      const bar = withGuide ? `${styleText(barColor, S_BAR)}  ` : ''
      const barEnd = withGuide ? styleText(barColor, S_BAR_END) : ''
      const noMatch = this.filteredOptions.length === 0 && userInput
        ? [`${bar}${styleText('yellow', '无匹配项')}`]
        : []
      const errLines = this.state === 'error'
        ? [`${bar}${styleText('yellow', this.error)}`]
        : []

      const header = [...headerBase]
      if (withGuide) header.push(`${bar.trimEnd()}`)
      header.push(
        `${bar}${styleText('dim', 'Search:')}${searchDisplay}${matchHint}`,
        ...noMatch,
        ...errLines,
      )

      const cols = getColumns(opts.output ?? process.stdout)
      const contentWidth = Math.max(cols - (withGuide ? 10 : 6), 20)
      const descPanel = buildDescPanel(
        resolveDescription(this.filteredOptions, this.focusedValue),
        bar,
        contentWidth,
      )
      const instructions = [
        `${styleText('dim', '↑/↓')} to select`,
        `${styleText('dim', 'Enter:')} confirm`,
        `${styleText('dim', 'Type:')} to search`,
      ]
      const footer = [
        `${bar}${styleText('dim', S_BAR_H())}`,
        ...descPanel,
        `${bar}${instructions.join(' · ')}`,
        barEnd,
      ].filter(Boolean)

      const listLines = this.filteredOptions.length === 0
        ? []
        : limitOptions({
          cursor: this.cursor,
          options: this.filteredOptions,
          maxItems: opts.maxItems,
          output: opts.output,
          columnPadding: withGuide ? 3 : 0,
          rowPadding: header.length + footer.length,
          style: (opt, active) => {
            const label = optionLabel(opt)
            if (opt.disabled) {
              return `${styleText('gray', S_RADIO_INACTIVE)} ${styleText(['strikethrough', 'gray'], label)}`
            }
            if (active) {
              return `${styleText('green', S_RADIO_ACTIVE)} ${label}`
            }
            return `${styleText('dim', S_RADIO_INACTIVE)} ${styleText('dim', label)}`
          },
        })

      return [
        ...header,
        ...listLines.map(line => `${bar}${line}`),
        ...footer,
      ].join('\n')
    },
  })

  return prompt.prompt()
}
