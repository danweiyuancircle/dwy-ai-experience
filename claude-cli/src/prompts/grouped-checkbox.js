import {
  createPrompt,
  useState,
  useMemo,
  useKeypress,
  usePrefix,
  usePagination,
  isUpKey,
  isDownKey,
  isSpaceKey,
  isBackspaceKey,
  isEnterKey,
  makeTheme,
} from '@inquirer/core'
import chalk from 'chalk'

const OTHER = '其他'

function sortCategories(cats) {
  const others = cats.includes(OTHER) ? [OTHER] : []
  const rest = cats.filter(c => c !== OTHER).sort((a, b) => a.localeCompare(b, 'zh'))
  return [...rest, ...others]
}

function buildVisibleRows(items, filter, selected) {
  const kw = filter.toLowerCase()
  const filtered = kw
    ? items.filter(it => it.name.toLowerCase().includes(kw)
                      || (it.description || '').toLowerCase().includes(kw))
    : items
  const groups = new Map()
  for (const it of filtered) {
    const cat = it.category || OTHER
    if (!groups.has(cat)) groups.set(cat, [])
    groups.get(cat).push(it)
  }
  const rows = []
  for (const cat of sortCategories([...groups.keys()])) {
    const groupItems = groups.get(cat).sort((a, b) => a.name.localeCompare(b.name))
    const selectedInGroup = groupItems.filter(it => selected.has(it.name)).length
    rows.push({ type: 'header', category: cat, total: groupItems.length, selectedInGroup, items: groupItems })
    for (const it of groupItems) rows.push({ type: 'item', item: it, category: cat })
  }
  return rows
}

function isPrintable(key) {
  return typeof key.sequence === 'string'
    && key.sequence.length === 1
    && key.sequence >= ' '
    && key.sequence <= '~'
    && !key.ctrl
    && !key.meta
    && key.name !== 'space'
    && key.name !== 'return'
    && key.name !== 'enter'
}

function isEscapeKey(key) {
  return key.name === 'escape'
}

function isCtrlA(key) {
  return key.ctrl && key.name === 'a'
}

function nextCursor(rows, cursor, delta) {
  if (rows.length === 0) return 0
  const n = rows.length
  let i = ((cursor + delta) % n + n) % n
  // 防止死循环（理论上 rows 永不为空时不会触发）
  return i
}

export const groupedCheckbox = createPrompt((config, done) => {
  const theme = makeTheme(config.theme)
  const pageSize = config.pageSize ?? 15
  const allItems = config.items
  const totalCount = allItems.length

  const [filter, setFilter] = useState('')
  const [cursor, setCursor] = useState(0)
  const [selected, setSelected] = useState(new Set(config.defaultSelected ?? []))
  const [status, setStatus] = useState('idle') // 'idle' | 'done'

  const rows = useMemo(
    () => buildVisibleRows(allItems, filter, selected),
    [filter, selected],
  )

  // cursor 越界保护
  const safeCursor = rows.length === 0 ? 0 : Math.min(cursor, rows.length - 1)

  useKeypress((key) => {
    if (status === 'done') return

    if (isEnterKey(key)) {
      const result = allItems.filter(it => selected.has(it.name))
      setStatus('done')
      done(result)
      return
    }

    if (isEscapeKey(key)) {
      if (filter) {
        setFilter('')
        setCursor(0)
      } else {
        setStatus('done')
        done([])
      }
      return
    }

    if (isUpKey(key)) {
      setCursor(nextCursor(rows, safeCursor, -1))
      return
    }
    if (isDownKey(key)) {
      setCursor(nextCursor(rows, safeCursor, +1))
      return
    }

    if (isCtrlA(key)) {
      // 全选/全不选当前可见 item
      const visibleItems = rows.filter(r => r.type === 'item').map(r => r.item)
      if (visibleItems.length === 0) return
      const allSelected = visibleItems.every(it => selected.has(it.name))
      const next = new Set(selected)
      if (allSelected) visibleItems.forEach(it => next.delete(it.name))
      else visibleItems.forEach(it => next.add(it.name))
      setSelected(next)
      return
    }

    if (isSpaceKey(key)) {
      if (rows.length === 0) return
      const row = rows[safeCursor]
      const next = new Set(selected)
      if (row.type === 'item') {
        if (next.has(row.item.name)) next.delete(row.item.name)
        else next.add(row.item.name)
      } else {
        // header：组内全选/全不选
        const allSelected = row.items.every(it => next.has(it.name))
        if (allSelected) row.items.forEach(it => next.delete(it.name))
        else row.items.forEach(it => next.add(it.name))
      }
      setSelected(next)
      return
    }

    if (isBackspaceKey(key)) {
      if (filter) {
        setFilter(filter.slice(0, -1))
        setCursor(0)
      }
      return
    }

    if (isPrintable(key)) {
      setFilter(filter + key.sequence)
      setCursor(0)
      return
    }
  })

  const prefix = usePrefix({ theme })

  if (status === 'done') {
    const picked = allItems.filter(it => selected.has(it.name))
    const summary = picked.length === 0
      ? chalk.gray('（未选）')
      : chalk.green(`已选 ${picked.length} 项`)
    return `${prefix} ${theme.style.message(config.message, 'done')} ${summary}`
  }

  const filterLine = filter
    ? `${chalk.cyan('🔍')} ${chalk.yellow(filter)}${chalk.gray('▏')}  ${chalk.gray(`${rows.filter(r => r.type === 'item').length}/${totalCount} 匹配`)}`
    : `${chalk.gray('🔍 输入即过滤  ')}${chalk.gray(`${totalCount} 项`)}`

  const hint = chalk.gray('↑↓ 移动 · space 切换/组全选 · ctrl+a 全选可见 · enter 确认 · esc 清搜索/退出')

  const renderItem = ({ item: row, isActive }) => {
    if (row.type === 'header') {
      const fullSelected = row.selectedInGroup === row.total && row.total > 0
      const partial = row.selectedInGroup > 0 && !fullSelected
      const marker = fullSelected ? chalk.green('✓') : partial ? chalk.yellow('◐') : chalk.gray('○')
      const arrow = isActive ? chalk.cyan('▶') : ' '
      const label = chalk.bold(`${arrow} ${marker} ${row.category}`)
      const count = chalk.gray(`[${row.selectedInGroup}/${row.total}]`)
      return isActive ? chalk.bgGray.white(`${label} ${count}`) : `${label} ${count}`
    }
    const checked = selected.has(row.item.name)
    const box = checked ? chalk.green('◉') : chalk.gray('◯')
    const cursorMark = isActive ? chalk.cyan('❯') : ' '
    const name = checked ? chalk.green(row.item.name) : chalk.cyan(row.item.name)
    const desc = row.item.description || ''
    const descShort = desc.length > 60 ? desc.slice(0, 60) + '…' : desc
    const line = `  ${cursorMark} ${box} ${name} ${chalk.gray('- ' + descShort)}`
    return isActive ? chalk.bgBlackBright(line) : line
  }

  const paginated = usePagination({
    items: rows.length > 0 ? rows : [{ type: 'empty' }],
    active: safeCursor,
    renderItem: (ctx) => ctx.item.type === 'empty'
      ? chalk.gray('  （无匹配项，按 esc 清空搜索）')
      : renderItem(ctx),
    pageSize,
    loop: false,
  })
  const page = paginated

  const message = theme.style.message(config.message, 'idle')

  return [
    `${prefix} ${message}`,
    filterLine,
    page,
    hint,
  ].join('\n')
})
