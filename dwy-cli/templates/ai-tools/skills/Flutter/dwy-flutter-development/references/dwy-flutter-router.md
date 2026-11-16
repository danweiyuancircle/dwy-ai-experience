# 路由与导航

涉及导航时，先读取官方 [flutter-setup-declarative-routing](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-setup-declarative-routing/SKILL.md)，再根据项目规模和已有依赖应用；该 Skill 面向声明式/深链场景，不代表每个简单页面都必须新增 GoRouter。

- 路由表、依赖注入、根导航状态属于 Assembly。Feature 不直接 import 另一 Feature 的页面，由装配层协调目的地。
- 简单应用可使用 SDK Navigator/Router；复杂深链、多导航栈或 Web 历史需求按已选路由库实现。弹窗和返回操作不因统一规范被无意义重写。
- 访客可用的功能不能被全局登录 redirect 意外拦截；认证守卫按产品规则挂载。
- 深链路径、查询、文件/分享 URI 是外部输入：验证缺失参数、格式和授权，提供可理解的无效目标状态，不用强制解包和未校验的 parse。
- 验证 Android 系统返回/预测性返回、iOS 返回、弹层关闭、根路由退出，以及有状态标签页切换。运行在 iPhone 上不会自动把整个 Material 页面替换成 Cupertino。
- 平台插件发来的深链和分享事件可能在冷启动或前台到达，避免重复消费；事件订阅由明确生命周期持有者释放。
