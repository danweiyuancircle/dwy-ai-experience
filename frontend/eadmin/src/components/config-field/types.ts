/**
 * 配置项控件的描述。
 * 不认具体业务字段。字节换算由页面传入，组件不带单位表。
 */

/** 一个下拉项。value 不能是空串。 */
export interface ConfigFieldOption {
  /** 显示文案。示例：``'MB'``。 */
  label: string
  /** 提交值。示例：``'MB'``。 */
  value: string
}

/** 控件种类。byte 存字节，duration 存秒，date 存 YYYY-MM-DD。 */
export type ConfigFieldKind = 'string' | 'int' | 'float' | 'bool' | 'enum' | 'byte' | 'duration' | 'date'

/** 一个配置项该画成哪种控件。 */
export interface ConfigFieldSpec {
  /** 控件种类。 */
  kind: ConfigFieldKind
  /** 日期能否清空。不传则可以。 */
  required?: boolean
  /** 数值下限。字节字段是字节，不是当前单位下的数字。示例：``1``。 */
  min?: number | null
  /** 数值上限。含义同 min。示例：``100``。 */
  max?: number | null
  /** 字符串最长字符数。示例：``32``。 */
  maxLength?: number | null
  /** enum 选项。kind 为 enum 时使用。 */
  options?: ConfigFieldOption[]
  /** 字节单位选项。kind 为 byte 时使用。 */
  unitOptions?: ConfigFieldOption[]
  /**
   * 字节框的小数位。
   * kind 为 byte 时由页面按当前单位给。示例：``2``。
   */
  precision?: number
  /**
   * 字节转成当前单位下的数字。
   * kind 为 byte 时必填。示例：``(bytes, unit) => bytes / 1048576``。
   */
  fromBytes?: (bytes: number, unit: string) => number
  /**
   * 当前单位下的数字转回字节。
   * kind 为 byte 时必填。示例：``(amount, unit) => amount * 1048576``。
   */
  toBytes?: (amount: number, unit: string) => number
}
