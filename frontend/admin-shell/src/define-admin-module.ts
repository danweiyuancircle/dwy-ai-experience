/**
 * 定义并归一化 AdminModule
 * 补默认 order / showInMenu，保证 createAdminShell 入参形状一致。
 */
import { DEFAULT_MODULE_ORDER } from './model/constants'
import type { AdminModule } from './model/types'

/**
 * 定义管理系统模块（补默认字段后原样返回，便于链式装配）。
 *
 * Args:
 *   module (AdminModule): 模块描述。id 必填；routes 必填（可为空数组）。示例：`{ id: 'quota', routes: [...] }`。
 * Returns:
 *   AdminModule: 写入默认 order / showInMenu 后的模块对象。
 */
export function defineAdminModule(module: AdminModule): AdminModule {
  return {
    ...module,
    order: module.order ?? DEFAULT_MODULE_ORDER,
    showInMenu: module.showInMenu ?? true,
  }
}
