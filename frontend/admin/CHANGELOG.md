# @dwydev/admin-kit

## 0.1.1

### Patch Changes

- 修正 npm 包名与首发可见性（`@dwydev/admin-kit`）

## 0.1.0

### Minor Changes

- 首版通用后台管理系统骨架，包名 **`@dwydev/admin-kit`**（npm 上 `@dwydev/admin` 不可用；与 `@dwydev/admin-shell` 并存）
  - `createAdminShell` / `defineAdminModule`：模块注册菜单（含 children 子菜单）与路由
  - `AdminShell` 内置 chrome：主题切换、通知 Popover、用户下拉、面包屑 / PageHero
  - `features` 开关：可关 theme / notifications / userMenu，兼容业务自管顶栏
  - `logoTo`、内容区 Hero 固定滚动（对齐 quant-cloud 布局习惯）
