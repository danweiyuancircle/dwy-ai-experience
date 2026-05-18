---
description: Flutter GoRouter 路由规范
category: Flutter
paths:
  - "**/app.dart"
  - "**/router/**/*.dart"
  - "**/routes/**/*.dart"
---

# Flutter 路由规范

## 一、路由（GoRouter）

### 1.1 路由定义

```dart
// app.dart 或 shared/providers/router_provider.dart
@riverpod
GoRouter router(Ref ref) {
  final auth = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = auth.isAuthenticated;
      final isLoginRoute = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLoginRoute) return '/login';
      if (isLoggedIn && isLoginRoute) return '/';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(
            path: '/',
            builder: (context, state) => const HomePage(),
          ),
          GoRoute(
            path: '/users',
            builder: (context, state) => const UserListPage(),
          ),
          GoRoute(
            path: '/users/:id',
            builder: (context, state) {
              final id = int.parse(state.pathParameters['id']!);
              return UserDetailPage(userId: id);
            },
          ),
        ],
      ),
    ],
  );
}
```

### 1.2 导航

```dart
// 声明式导航
context.go('/users');            // 替换当前页面栈
context.push('/users/123');      // 压入新页面
context.pop();                   // 返回

// 禁止使用 Navigator.push / Navigator.pushNamed
```

### 1.3 底部导航（StatefulShellRoute）

```dart
StatefulShellRoute.indexedStack(
  builder: (context, state, navigationShell) {
    return ScaffoldWithBottomNav(navigationShell: navigationShell);
  },
  branches: [
    StatefulShellBranch(routes: [
      GoRoute(path: '/home', builder: (_, __) => const HomePage()),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: '/profile', builder: (_, __) => const ProfilePage()),
    ]),
  ],
)
```

### 1.4 路由规则

| 规则 | 说明 |
|------|------|
| 全部用 GoRouter | 禁止 `Navigator.push` / `Navigator.pushNamed` |
| 认证守卫在 redirect 中 | 不在每个页面单独检查 |
| 路径参数用 `:id` | `/users/:id`，通过 `state.pathParameters['id']` 获取 |
| 查询参数用 `state.uri.queryParameters` | 分页、筛选等 |
