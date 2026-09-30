# Changelog

## 0.2.0

### Changed

- 以 quant-cloud 控制台实战版为基座整体重写：AdminShell 收敛为「meta 驱动 + header-center/extra 插槽」,
  不再内置用户菜单 / 通知 / 主题 chrome（宿主经插槽自行组装,与 quant-cloud 用法一致）
- logoTo / collapsedStorageKey / PageHero 壳级页级双开关 / 面包屑末项去链接 / header 插槽 pointer-events 穿透

### Added

- `CreateAdminShellOptions.menuFilter`:侧栏菜单角色过滤谓词(只裁菜单不动路由)
- `asMenuIcon`:lucide 组件 → eui MenuItem.icon 类型收口
- 自带 vitest 单测(路径归一 / 菜单 order / meta 合并 / menuFilter)

### Removed

- `features`(theme/notifications/userMenu)与 `theme.css` —— 破坏性变更,宿主改经插槽组装

## 0.1.0

### Added

- 初版：`createAdminShell` / `defineAdminModule` 模块装配
- `AdminShell`（基于 eui `EAdminLayout`）+ `#header-extra` + 折叠持久化
- `AdminPageHero` / `AdminBreadcrumb` / `AdminPageHeader`（meta 驱动页头）
- `showInMenu` / `menuKey` / `pageHero` / `breadcrumb` 约定
