import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export { dayjs }

type DateInput = string | number | Date

/**
 * Format a date string or timestamp to relative time (Chinese).
 * "刚刚", "5 分钟前", "3 小时前", "2 天前", or formatted date.
 */
export function formatRelativeTime(dateInput: DateInput): string {
  if (!dateInput) return ''
  const target = dayjs(dateInput)
  const now = dayjs()
  const diffMin = now.diff(target, 'minute')

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = now.diff(target, 'hour')
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = now.diff(target, 'day')
  if (diffDay < 30) return `${diffDay} 天前`
  return target.format('YYYY-MM-DD')
}

/**
 * Format date to YYYY-MM-DD
 */
export function formatDate(dateInput: DateInput): string {
  return dayjs(dateInput).format('YYYY-MM-DD')
}

/**
 * Format date to YYYY-MM-DD HH:mm:ss
 */
export function formatDateTime(dateInput: DateInput): string {
  return dayjs(dateInput).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * Format time to HH:mm
 */
export function formatTime(dateInput: DateInput): string {
  return dayjs(dateInput).format('HH:mm')
}

/**
 * Format date with custom template
 */
export function formatBy(dateInput: DateInput, template: string): string {
  return dayjs(dateInput).format(template)
}
