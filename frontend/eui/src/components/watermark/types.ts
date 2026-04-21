/**
 * EWatermark 水印组件类型定义
 */

/** EWatermark Props */
export interface EWatermarkProps {
  /** 自定义类名 */
  class?: string
  /** 水印文本；数组形式可渲染多行 */
  content?: string | string[]
  /** 字号（px），默认 14 */
  fontSize?: number
  /** 旋转角度（度），默认 -30 */
  rotate?: number
  /** 文字间距 [水平, 垂直]，默认 [100, 100] */
  gap?: [number, number]
  /** 透明度 0-1，默认 0.15 */
  opacity?: number
}
