/**
 * 日期格式化工具
 * 基于 dayjs，默认加载中文语言包和相对时间插件；业务统一用这里导出的快捷函数，不直接 new Date / format
 */
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

// 启用相对时间插件（fromNow/toNow 等）并切换到中文语言环境
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export { dayjs }

/** 日期输入类型：ISO 字符串 / 时间戳（毫秒） / Date 对象 */
type DateInput = string | number | Date

/**
 * 格式化为中文相对时间（"刚刚"/"N 分钟前"/"N 小时前"/"N 天前"）
 * 超过 30 天则退化为 YYYY-MM-DD 绝对日期，避免出现"100 天前"这类不直观的描述
 * @param dateInput 时间（字符串/时间戳/Date）
 * @returns 人类可读的相对时间描述；空输入返回空字符串
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
 * 格式化为 YYYY-MM-DD
 * @param dateInput 时间（字符串/时间戳/Date）
 */
export function formatDate(dateInput: DateInput): string {
  return dayjs(dateInput).format('YYYY-MM-DD')
}

/**
 * 格式化为 YYYY-MM-DD HH:mm:ss
 * @param dateInput 时间（字符串/时间戳/Date）
 */
export function formatDateTime(dateInput: DateInput): string {
  return dayjs(dateInput).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * 格式化为 HH:mm
 * @param dateInput 时间（字符串/时间戳/Date）
 */
export function formatTime(dateInput: DateInput): string {
  return dayjs(dateInput).format('HH:mm')
}

/**
 * 按自定义模板格式化时间
 * @param dateInput 时间（字符串/时间戳/Date）
 * @param template dayjs 格式模板，如 'YYYY年MM月DD日'
 */
export function formatBy(dateInput: DateInput, template: string): string {
  return dayjs(dateInput).format(template)
}
