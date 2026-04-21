/**
 * Vue 插件安装辅助工具
 * 将组件映射批量注册为 Vue 全局组件，供各独立子包复用，避免重复样板代码
 */
import type { App, Component } from 'vue'

/**
 * 批量注册全局组件
 * @param app Vue 应用实例
 * @param components 组件名到组件定义的映射
 */
export function installComponents(app: App, components: Record<string, Component>) {
  for (const [name, component] of Object.entries(components)) {
    app.component(name, component)
  }
}
