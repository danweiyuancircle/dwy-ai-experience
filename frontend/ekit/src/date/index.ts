/**
 * 日期 / 时间工具
 * 内部基于 dayjs（+ utc、timezone、relativeTime 插件），对外只暴露 ekit 自有 API（number / string）
 * 底层库不对外泄露（无 dayjs 实例、无 dayjs.Dayjs 类型）
 */
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import utcPlugin from 'dayjs/plugin/utc'
import timezonePlugin from 'dayjs/plugin/timezone'
import 'dayjs/locale/zh-cn'

// timezone 依赖 utc；relativeTime 用于 formatRelativeTime
dayjs.extend(utcPlugin)
dayjs.extend(timezonePlugin)
dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

/** 日期输入类型：ISO 字符串 / 时间戳（毫秒） / Date 对象 */
type DateInput = string | number | Date

/** 默认格式模板 */
const DEFAULT_FORMAT = 'YYYY-MM-DD HH:mm:ss'

/**
 * 获取当前时刻的 UTC 时间戳（毫秒）
 * JavaScript 时间戳本身即为 UTC Unix epoch，数值不随时区变化
 * @returns Unix epoch 毫秒数
 */
export function now(): number {
  return dayjs().valueOf()
}

/**
 * 把时间戳格式化为字符串（本地时区）
 * @param timestamp Unix epoch 毫秒数
 * @param format 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的本地时间字符串
 */
export function formatTimestamp(timestamp: number, format: string = DEFAULT_FORMAT): string {
  return dayjs(timestamp).format(format)
}

/**
 * 把时间戳格式化为指定时区下的字符串
 * @param timezone IANA 时区名，如 'Asia/Shanghai' / 'America/New_York' / 'UTC' / 'Europe/London'
 * @param timestamp Unix epoch 毫秒数；不传则使用当前时间
 * @param format 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns 指定时区下格式化后的字符串
 */
export function formatInTimezone(
  timezone: string,
  timestamp?: number,
  format: string = DEFAULT_FORMAT,
): string {
  const base = timestamp === undefined ? dayjs() : dayjs(timestamp)
  return base.tz(timezone).format(format)
}

/**
 * 格式化为中文相对时间（"刚刚"/"N 分钟前"/"N 小时前"/"N 天前"）
 * 超过 30 天则退化为 YYYY-MM-DD 绝对日期，避免出现"100 天前"这类不直观的描述
 * @param dateInput 时间（字符串 / 时间戳 / Date）
 * @returns 人类可读的相对时间描述；空输入返回空字符串
 */
export function formatRelativeTime(dateInput: DateInput): string {
  if (!dateInput) return ''
  const target = dayjs(dateInput)
  const current = dayjs()
  const diffMin = current.diff(target, 'minute')

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = current.diff(target, 'hour')
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = current.diff(target, 'day')
  if (diffDay < 30) return `${diffDay} 天前`
  return target.format('YYYY-MM-DD')
}

/**
 * 格式化为 YYYY-MM-DD
 * @param dateInput 时间（字符串 / 时间戳 / Date）
 */
export function formatDate(dateInput: DateInput): string {
  return dayjs(dateInput).format('YYYY-MM-DD')
}

/**
 * 格式化为 YYYY-MM-DD HH:mm:ss
 * @param dateInput 时间（字符串 / 时间戳 / Date）
 */
export function formatDateTime(dateInput: DateInput): string {
  return dayjs(dateInput).format(DEFAULT_FORMAT)
}

/**
 * 格式化为 HH:mm
 * @param dateInput 时间（字符串 / 时间戳 / Date）
 */
export function formatTime(dateInput: DateInput): string {
  return dayjs(dateInput).format('HH:mm')
}

/**
 * 按自定义模板格式化时间
 * @param dateInput 时间（字符串 / 时间戳 / Date）
 * @param template dayjs 格式模板，如 'YYYY年MM月DD日'
 */
export function formatBy(dateInput: DateInput, template: string): string {
  return dayjs(dateInput).format(template)
}
