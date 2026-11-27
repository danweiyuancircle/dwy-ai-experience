/**
 * 确认后执行一次写操作。
 * 只认确认框和提示的最小接口，页面传入 useMessageBox / useMessage 的返回值。
 */

/** 确认框。取消时 resolve 为 ``'cancel'``。 */
export interface ConfirmBox {
  /**
   * 打开确认框。
   * @param message 正文。示例：``'确定下架？'``。
   * @param title 标题。示例：``'下架套餐'``。
   * @returns ``'confirm'`` 或 ``'cancel'``。
   */
  confirm: (message: string, title?: string) => Promise<'confirm' | 'cancel'>
}

/** 成功 / 失败提示。 */
export interface ConfirmToast {
  /**
   * 成功提示。
   * @param text 文案。示例：``'已下架'``。
   */
  success: (text: string) => void
  /**
   * 失败提示。
   * @param text 文案。示例：``'下架失败'``。
   */
  error: (text: string) => void
}

/**
 * 一次确认执行的参数。
 * success 可以是固定句子，也可以用 run 的返回值拼（清理条数这类）。
 */
export interface ConfirmThenOptions<T> {
  /** 确认框正文。示例：``'确定下架「专业版」？'``。 */
  message: string
  /** 确认框标题。示例：``'下架套餐'``。 */
  title: string
  /**
   * 成功文案。不传则成功时不提示。
   * 函数收到 run 的返回值。示例：``'已下架'``。
   */
  success?: string | ((value: T) => string)
  /**
   * 失败文案。函数收到 run 抛出的值，用来保留接口返回的业务句。
   * 示例：``'下架失败'``。
   */
  failure: string | ((error: unknown) => string)
  /**
   * 用户点确定后执行。抛错视为失败。
   * 加载中的开关放在这里，用 try/finally，不要把错误吞掉。
   */
  run: () => Promise<T>
}
