/**
 * 顶部 Tab + 下方多选。
 * 每个 Tab 一组子项；←/→ 切 Tab，↑/↓ + Space 勾当前组，a 全选/清空当前 Tab。
 * 基于 @clack/core Prompt 自绘，不引入新 UI 库。
 */

import { Prompt, getColumns, settings } from '@clack/core'
import { limitOptions } from '@clack/prompts'
import { styleText } from 'node:util'
import process from 'node:process'

/** 是否支持 unicode 符号（与 clack / searchable-select 判定一致） */
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
const S_BAR_H = () => unicodeOr('─', '-')
const S_CHECKBOX_SELECTED = unicodeOr('◼', '[+]')
const S_CHECKBOX_INACTIVE = unicodeOr('◻', '[ ]')
const S_TAB_MORE = unicodeOr('‹', '<')
const S_TAB_MORE_RIGHT = unicodeOr('›', '>')

/**
 * skill / rule / hook 的终端标记。
 * 不用 emoji：几何符号 + 固定宽度英文，无 unicode 时退回 S/R/H。
 */
const ITEM_TYPE_META = {
  skills: { icon: unicodeOr('◈', 'S'), word: 'skill', color: 'cyan', title: '技能' },
  rules: { icon: unicodeOr('☰', 'R'), word: 'rule', color: 'yellow', title: '规则' },
  hooks: { icon: unicodeOr('⤷', 'H'), word: 'hook', color: 'magenta', title: '钩子' },
}

/**
 * 取类型展示元数据。未知类型当 skill，避免列表画出空白标记。
 *
 * @param {string | undefined} type
 */
export function itemTypeMeta(type) {
  return ITEM_TYPE_META[type] || ITEM_TYPE_META.skills
}

/**
 * 行首类型前缀：图标 + 对齐后的 skill/rule/hook。
 *
 * @param {string | undefined} type
 */
export function formatItemTypePrefix(type) {
  const meta = itemTypeMeta(type)
  return `${styleText(meta.color, meta.icon)} ${styleText(meta.color, meta.word.padEnd(5, ' '))}`
}

/** Tab 之间空格数。过密会糊成一行，过疏又浪费宽度。 */
const TAB_GAP = 2
/** 省略角标占位。‹/› 按 1 列计。 */
const ELLIPSIS_W = 1
/**
 * 技术栈 / 场景分组之间插入 `  |  ` 比普通间隙多出来的宽度。
 * 普通间隙 TAB_GAP=2；再加 `|` 和一侧间隙 → 3。
 */
const GROUP_SEP_EXTRA = 1 + TAB_GAP

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
 * 本 Tab 已勾数 / 总数。只数该 Tab 自己的 value，跨 Tab 同名不影响。
 *
 * @param {{ options: { value: unknown }[] }} tab
 * @param {Iterable<unknown>} selectedValues
 */
export function tabSelectionStats(tab, selectedValues) {
  const set = selectedValues instanceof Set ? selectedValues : new Set(selectedValues)
  const total = tab.options.length
  const selected = tab.options.filter(option => set.has(option.value)).length
  return { selected, total }
}

/**
 * Tab 栏纯文本（无样式），格式 `标签 已选/总数`。
 *
 * @param {Array<{ label: string, options: { value: unknown }[] }>} tabs
 * @param {Iterable<unknown>} selectedValues
 */
export function tabBarSegments(tabs, selectedValues) {
  const set = selectedValues instanceof Set ? selectedValues : new Set(selectedValues)
  return tabs.map((tab) => {
    const { selected, total } = tabSelectionStats(tab, set)
    return `${tab.label} ${selected}/${total}`
  })
}

/**
 * 窗口内因 group 切换而多出来的分隔宽度。
 *
 * @param {string[] | undefined} groups
 * @param {number} start
 * @param {number} end
 */
function groupSepWidth(groups, start, end) {
  if (!groups) return 0
  let extra = 0
  for (let i = start + 1; i < end; i++) {
    if (groups[i] && groups[i - 1] && groups[i] !== groups[i - 1]) extra += GROUP_SEP_EXTRA
  }
  return extra
}

/**
 * 以当前 Tab 为中心裁出能放进 maxWidth 的窗口。
 * 约束：当前段永远保留；连当前段都超宽也只露出这一段（交给渲染截断）。
 *
 * @param {string[]} segments
 * @param {number} activeIndex
 * @param {number} maxWidth
 * @param {string[]} [groups] 与 segments 等长；相邻不同则预留 `|` 分隔宽
 */
export function tabWindow(segments, activeIndex, maxWidth, groups) {
  const n = segments.length
  if (n === 0) return { start: 0, end: 0, showLeft: false, showRight: false }
  const idx = Math.min(Math.max(activeIndex, 0), n - 1)
  const widths = segments.map(segment => segment.length)

  const used = (start, end) => {
    let w = 0
    for (let i = start; i < end; i++) {
      if (i > start) w += TAB_GAP
      w += widths[i]
    }
    w += groupSepWidth(groups, start, end)
    if (start > 0) w += ELLIPSIS_W + TAB_GAP
    if (end < n) w += TAB_GAP + ELLIPSIS_W
    return w
  }

  let start = idx
  let end = idx + 1
  // 当前段已经超宽：不再扩张，避免把邻 Tab 挤没
  if (used(start, end) > maxWidth) {
    return { start, end, showLeft: start > 0, showRight: end < n }
  }

  let grew = true
  while (grew) {
    grew = false
    if (end < n && used(start, end + 1) <= maxWidth) {
      end += 1
      grew = true
    }
    if (start > 0 && used(start - 1, end) <= maxWidth) {
      start -= 1
      grew = true
    }
  }
  return { start, end, showLeft: start > 0, showRight: end < n }
}

/**
 * a 键：当前 Tab 未全勾则补全，已全勾则清空。其它 Tab 的勾选不动。
 *
 * @param {unknown[]} selectedValues
 * @param {unknown[]} tabValues
 */
export function toggleTabValues(selectedValues, tabValues) {
  const set = new Set(selectedValues)
  const allOn = tabValues.length > 0 && tabValues.every(value => set.has(value))
  if (allOn) {
    const drop = new Set(tabValues)
    return selectedValues.filter(value => !drop.has(value))
  }
  return [...new Set([...selectedValues, ...tabValues])]
}

/**
 * 打开时落在第一个已有勾选的 Tab，方便接着改；全空则 0。
 *
 * @param {Array<{ options: { value: unknown }[] }>} tabs
 * @param {unknown[]} selectedValues
 */
export function firstTabWithSelection(tabs, selectedValues) {
  if (!tabs.length) return 0
  const set = new Set(selectedValues)
  const idx = tabs.findIndex(tab => tab.options.some(option => set.has(option.value)))
  return idx >= 0 ? idx : 0
}

/**
 * 顶部 Tab + 下方 checkbox 的 Prompt。
 * trackValue=false：字母键不当输入，留给 a 全选。
 */
class TabMultiSelectPrompt extends Prompt {
  /** @type {Array<{ id: string, label: string, options: object[] }>} */
  tabs
  tabIndex = 0
  /** 每个 Tab 记住光标，切走再回来不丢位置 */
  cursors = []

  get currentTab() {
    return this.tabs[this.tabIndex]
  }

  get currentOptions() {
    return this.currentTab?.options ?? []
  }

  get cursor() {
    return this.cursors[this.tabIndex] ?? 0
  }

  set cursor(index) {
    this.cursors[this.tabIndex] = index
  }

  constructor(opts) {
    super(opts, false)
    this.tabs = opts.tabs
    this.value = [...(opts.initialValues ?? [])]
    this.cursors = this.tabs.map(() => 0)
    this.tabIndex = firstTabWithSelection(this.tabs, this.value)
    this.on('cursor', (action) => this.#onCursor(action))
    this.on('key', (_ch, key) => {
      if (key?.name === 'a') this.toggleAllCurrentTab()
    })
  }

  /** ←/→ 切 Tab；↑/↓ 在当前组移动；Space 勾当前项。 */
  #onCursor(action) {
    const len = this.currentOptions.length
    switch (action) {
      case 'left':
        if (this.tabs.length === 0) return
        this.tabIndex = (this.tabIndex - 1 + this.tabs.length) % this.tabs.length
        return
      case 'right':
        if (this.tabs.length === 0) return
        this.tabIndex = (this.tabIndex + 1) % this.tabs.length
        return
      case 'up':
        if (len === 0) return
        this.cursor = (this.cursor - 1 + len) % len
        return
      case 'down':
        if (len === 0) return
        this.cursor = (this.cursor + 1) % len
        return
      case 'space':
        this.toggleValue()
    }
  }

  /** Space：只动光标那一条。 */
  toggleValue() {
    const option = this.currentOptions[this.cursor]
    if (!option) return
    const selected = this.value.includes(option.value)
    this.value = selected
      ? this.value.filter(value => value !== option.value)
      : [...this.value, option.value]
  }

  /** a：当前 Tab 全选或全不选。 */
  toggleAllCurrentTab() {
    const tabValues = this.currentOptions.map(option => option.value)
    this.value = toggleTabValues(this.value, tabValues)
  }
}

/**
 * 画 Tab 栏。当前 Tab 反底；有勾选的其它 Tab 用青色，空的变暗。
 *
 * @param {string[]} segments
 * @param {number} activeIndex
 * @param {ReturnType<typeof tabWindow>} win
 * @param {Array<{ options: { value: unknown }[] }>} tabs
 * @param {unknown[]} selectedValues
 */
function renderTabBar(segments, activeIndex, win, tabs, selectedValues) {
  const set = new Set(selectedValues)
  const parts = []
  if (win.showLeft) parts.push(styleText('dim', S_TAB_MORE))
  for (let i = win.start; i < win.end; i++) {
    if (i > win.start && tabs[i].group && tabs[i - 1].group && tabs[i].group !== tabs[i - 1].group) {
      parts.push(styleText('dim', '|'))
    }
    const text = segments[i]
    const { selected } = tabSelectionStats(tabs[i], set)
    if (i === activeIndex) {
      parts.push(styleText(['bgCyan', 'black'], ` ${text} `))
    } else if (selected > 0) {
      parts.push(styleText('cyan', text))
    } else {
      parts.push(styleText('dim', text))
    }
  }
  if (win.showRight) parts.push(styleText('dim', S_TAB_MORE_RIGHT))
  return parts.join(' '.repeat(TAB_GAP))
}

/**
 * 打开顶部 Tab + 下方多选。
 * tabs 为空时不进交互，直接返回 []（调用方应先过滤空包）。
 *
 * @param {object} opts
 * @param {string} opts.message
 * @param {Array<{ id: string, label: string, options: Array<{ value: unknown, label?: string, description?: string }> }>} opts.tabs
 * @param {unknown[]} [opts.initialValues]
 * @param {boolean} [opts.required]
 * @param {number} [opts.maxItems]
 * @returns {Promise<unknown[] | symbol>}
 */
export function tabMultiselect(opts) {
  if (!opts.tabs || opts.tabs.length === 0) return Promise.resolve([])

  const withGuide = opts.withGuide ?? settings.withGuide
  const prompt = new TabMultiSelectPrompt({
    tabs: opts.tabs,
    initialValues: opts.initialValues,
    signal: opts.signal,
    input: opts.input,
    output: opts.output,
    validate: () => {
      if (opts.required && (!prompt.value || prompt.value.length === 0)) {
        return '请至少选择一项'
      }
    },
    render() {
      const selected = this.value ?? []
      const msgLine = `${withGuide ? `${styleText('gray', S_BAR)}\n` : ''}${symbol(this.state)}  ${opts.message}\n`

      if (this.state === 'submit') {
        return `${msgLine}${withGuide ? `${styleText('gray', S_BAR)}  ` : ''}${styleText(
          'dim',
          `已选 ${selected.length} 项`,
        )}`
      }
      if (this.state === 'cancel') {
        return `${msgLine}${withGuide ? `${styleText('gray', S_BAR)}  ` : ''}${styleText(['strikethrough', 'dim'], '已取消')}`
      }

      const barColor = this.state === 'error' ? 'yellow' : 'cyan'
      const bar = withGuide ? `${styleText(barColor, S_BAR)}  ` : ''
      const barEnd = withGuide ? styleText(barColor, S_BAR_END) : ''
      const errLines = this.state === 'error'
        ? [`${bar}${styleText('yellow', this.error)}`]
        : []

      const cols = getColumns(opts.output ?? process.stdout)
      const contentWidth = Math.max(cols - (withGuide ? 10 : 6), 20)
      const segments = tabBarSegments(this.tabs, selected)
      const groups = this.tabs.map(tab => tab.group)
      const win = tabWindow(segments, this.tabIndex, contentWidth, groups)
      const tabLine = renderTabBar(segments, this.tabIndex, win, this.tabs, selected)

      const focused = this.currentOptions[this.cursor]
      const focusedType = itemTypeMeta(focused?.type)
      const descRaw = (focused?.description || '').trim() || '（无说明）'
      const desc = `${focusedType.title} · ${descRaw}`
      const instructions = [
        `${styleText('dim', '←/→')} 切 Tab`,
        `${styleText('dim', '↑/↓')} 移动`,
        `${styleText('dim', 'Space')} 勾选`,
        `${styleText('dim', 'a')} 全选本 Tab`,
        `${styleText('dim', 'Enter')} 确认`,
      ]

      const header = [
        ...`${msgLine}${withGuide ? styleText(barColor, S_BAR) : ''}`.split('\n'),
        `${bar}${tabLine}`,
        `${bar}${styleText('dim', S_BAR_H())}`,
        ...errLines,
      ]
      const footer = [
        `${bar}${styleText('dim', S_BAR_H())}`,
        `${bar}${styleText('dim', '说明：')}${styleText('dim', desc)}`,
        `${bar}${instructions.join(' · ')}`,
        barEnd,
      ]

      const options = this.currentOptions
      const listLines = options.length === 0
        ? [`${styleText('dim', '（本 Tab 无条目）')}`]
        : limitOptions({
          cursor: this.cursor,
          options,
          maxItems: opts.maxItems ?? 12,
          output: opts.output,
          rowPadding: header.length + footer.length,
          style: (opt, active) => {
            const on = selected.includes(opt.value)
            const label = opt.label ?? String(opt.value ?? '')
            const box = on
              ? styleText('green', S_CHECKBOX_SELECTED)
              : styleText('dim', S_CHECKBOX_INACTIVE)
            const prefix = formatItemTypePrefix(opt.type)
            if (active) return `${box} ${prefix} ${label}`
            return `${box} ${prefix} ${styleText('dim', label)}`
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
