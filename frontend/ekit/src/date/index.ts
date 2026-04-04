/**
 * Format a date string or timestamp to relative time (Chinese).
 * "刚刚", "5 分钟前", "3 小时前", "2 天前", or formatted date.
 */
export function formatRelativeTime(dateInput: string | number | Date): string {
  if (!dateInput) return ''
  const date = typeof dateInput === 'string' || typeof dateInput === 'number'
    ? new Date(dateInput)
    : dateInput
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 30) return `${diffDay} 天前`
  return date.toLocaleDateString('zh-CN')
}

/**
 * Format date to YYYY-MM-DD
 */
export function formatDate(dateInput: string | number | Date): string {
  const d = new Date(dateInput)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/**
 * Format date to YYYY-MM-DD HH:mm:ss
 */
export function formatDateTime(dateInput: string | number | Date): string {
  const d = new Date(dateInput)
  return `${formatDate(d)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

/**
 * Format time to HH:mm
 */
export function formatTime(dateInput: string | number | Date): string {
  const d = new Date(dateInput)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
