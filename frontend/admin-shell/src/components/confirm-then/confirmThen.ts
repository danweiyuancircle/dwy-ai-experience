/**
 * 确认后执行，成功或失败只提示一次。
 *
 * 取消不调用 run。run 抛错不再向上抛：各页原来都是自己 catch 后 toast，
 * 收口后页面不再包一层 try/catch。业务错误句由 failure 函数自己取。
 */
import type { ConfirmBox, ConfirmThenOptions, ConfirmToast } from './types'

/**
 * 弹出确认框，确定后执行 run。
 * @param box 确认框。示例：``useMessageBox()``。
 * @param toast 提示。示例：``useMessage()``。
 * @param options 文案与执行函数。
 * @returns 执行成功为 true。取消或失败为 false。
 */
export async function confirmThen<T>(
  box: ConfirmBox,
  toast: ConfirmToast,
  options: ConfirmThenOptions<T>,
): Promise<boolean> {
  const choice = await box.confirm(options.message, options.title)
  if (choice !== 'confirm') return false
  try {
    const value = await options.run()
    notifySuccess(toast, options.success, value)
    return true
  } catch (error) {
    toast.error(resolveFailure(options.failure, error))
    return false
  }
}

/**
 * 成功时按字符串或返回值提示。没配成功文案则安静结束。
 * @param toast 提示入口。
 * @param success 固定文案，或用返回值拼文案。不传则不提示。
 * @param value run 的返回值。
 */
function notifySuccess<T>(
  toast: ConfirmToast,
  success: ConfirmThenOptions<T>['success'],
  value: T,
): void {
  if (success === undefined) return
  if (typeof success === 'function') {
    toast.success(success(value))
    return
  }
  toast.success(success)
}

/**
 * 失败文案。函数形态用来带上接口返回的业务句。
 * @param failure 固定句子，或根据抛出值生成句子。
 * @param error run 抛出的值。
 * @returns 给用户看的失败句。
 */
function resolveFailure(
  failure: string | ((error: unknown) => string),
  error: unknown,
): string {
  if (typeof failure === 'function') return failure(error)
  return failure
}
