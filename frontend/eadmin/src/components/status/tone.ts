/**
 * 后台状态徽章的七档色。
 * 身份和生命周期分开，避免「特殊身份」和「正在生效」撞成同一个主色。
 * 类名必须写全：Tailwind 只扫描字面量。文案由页面自己定，这张表只给色。
 */

/** 七档语义色。浅底深字，表格里不刺眼。 */
export const STATUS_TONE = {
  /** 需要和普通身份分开的那一档。不表示生效。 */
  identity: 'border-transparent bg-indigo-100 text-indigo-800',
  /** 默认身份，以及说不清的状态。 */
  neutral: 'border-transparent bg-secondary text-secondary-foreground',
  /** 正在生效，或已经完成。 */
  active: 'border-transparent bg-emerald-100 text-emerald-800',
  /** 还没完成。 */
  pending: 'border-transparent bg-amber-100 text-amber-900',
  /** 人为关掉，记录还在，可以恢复。 */
  stopped: 'border-transparent bg-rose-100 text-rose-800',
  /** 出错。 */
  error: 'border-transparent bg-destructive text-white',
  /** 单独一档，不并进成功或失败。 */
  refund: 'border-border bg-transparent text-foreground',
} as const

export type StatusTone = keyof typeof STATUS_TONE

/**
 * 开着用生效色，关掉用停用色。
 * @param active 仍生效。示例：``true``。
 */
export function presenceClass(active: boolean): string {
  return active ? STATUS_TONE.active : STATUS_TONE.stopped
}

/**
 * 完成用生效色，未完成用待办色。
 * @param done 已经完成。示例：``false``。
 */
export function completionClass(done: boolean): string {
  return done ? STATUS_TONE.active : STATUS_TONE.pending
}
