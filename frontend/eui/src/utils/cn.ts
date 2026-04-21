/**
 * Tailwind class 合并工具
 * 先用 clsx 合并条件类名，再用 tailwind-merge 消除冲突（如 px-2 与 px-4 同时出现时保留后者）
 */
import type { ClassValue } from 'clsx'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * 合并任意 class 参数并去除 Tailwind 冲突
 * @param inputs 任意 clsx 支持的 class 输入（字符串/对象/数组/假值）
 * @returns 合并且去冲突后的最终 class 字符串
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
