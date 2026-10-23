/**
 * 分段筛选的一项。
 * 值必须是非空字符串：切换组用空串表示「点掉当前项」。
 */
export interface SegmentedOption {
  /** 按钮文案。示例：``'正常'``。 */
  label: string
  /** 选项值。示例：``'active'``。 */
  value: string
  /**
   * 跟在文案后的计数。
   * 不传则只显示文案。``0`` 也显示。示例：``12``。
   */
  count?: number
}
