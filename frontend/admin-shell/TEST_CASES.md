# @dwydev/admin-shell 测试用例

| 用例 | 文件 | 说明 |
|------|------|------|
| 相对 path 归一化为绝对 path | `tests/create-admin-shell.test.ts` | `quota` → `/quota` |
| 已是绝对 path 不重复前缀 | 同上 | `/keys` 保持 |
| 根 path 保持为 `/` | 同上 | `''` 与 `/` |
| 按 order 合并菜单并注入默认 meta | 同上 | 菜单顺序、children、requiresAuth/layout |
| showInMenu=false 只注册路由 | 同上 | 菜单无该项、routes 仍有 |
