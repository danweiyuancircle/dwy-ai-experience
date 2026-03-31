import type { App, Component } from 'vue'

export function installComponents(app: App, components: Record<string, Component>) {
  for (const [name, component] of Object.entries(components)) {
    app.component(name, component)
  }
}
