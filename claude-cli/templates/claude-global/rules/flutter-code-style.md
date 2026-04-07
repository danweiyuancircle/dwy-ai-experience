# Flutter + Dart 代码规范

本规范约束所有 Flutter 项目的代码风格、架构模式和最佳实践。与 `vue-code-style.md`、`python-code-style.md` 平级。

> 跨端通用约束（技术选型、API 格式、Docker、OSS 等）见 `engineering-tech-spec.md`。

---

## 一、项目结构

### 1.1 标准目录

```
project_name/
├── lib/
│   ├── main.dart                      # runApp + ProviderScope
│   ├── app.dart                       # MaterialApp.router + GoRouter + Theme
│   │
│   ├── core/                          # 全局基础设施（不含业务逻辑）
│   │   ├── config/
│   │   │   └── env.dart               # 环境配置（API 地址、OSS 端点等）
│   │   ├── network/
│   │   │   ├── dio_client.dart        # Dio 实例 + 全部拦截器
│   │   │   ├── api_response.dart      # 统一响应模型（对齐 eapi 格式）
│   │   │   └── interceptors/
│   │   │       ├── token_interceptor.dart
│   │   │       ├── refresh_interceptor.dart
│   │   │       ├── unwrap_interceptor.dart
│   │   │       └── error_interceptor.dart
│   │   ├── storage/
│   │   │   └── token_storage.dart     # FlutterSecureStorage 封装
│   │   ├── theme/
│   │   │   ├── app_theme.dart         # ThemeData（亮色 + 暗色）
│   │   │   └── app_colors.dart        # 设计 tokens
│   │   └── utils/                     # 通用工具（格式化、校验等）
│   │
│   ├── features/                      # 功能模块（feature-first 拆分）
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── auth_repository.dart
│   │   │   │   └── auth_dto.dart
│   │   │   ├── domain/
│   │   │   │   └── user_entity.dart
│   │   │   └── presentation/
│   │   │       ├── login_page.dart
│   │   │       ├── auth_provider.dart
│   │   │       └── widgets/
│   │   │           └── login_form.dart
│   │   ├── home/
│   │   │   └── ...
│   │   └── {feature_name}/
│   │       ├── data/                  # 数据层：Repository 实现 + DTO
│   │       ├── domain/                # 领域层：Entity（可选，简单场景直接用 DTO）
│   │       └── presentation/          # 表现层：Page + Provider + Widget
│   │
│   └── shared/                        # 跨功能共享
│       ├── providers/                 # 全局 Provider（auth、theme、dio）
│       ├── widgets/                   # 共享 Widget（AppBar、ErrorView 等）
│       └── models/                    # 共享数据模型
│
├── test/
│   ├── core/
│   ├── features/
│   │   └── {feature_name}/
│   └── shared/
│
├── pubspec.yaml
├── analysis_options.yaml              # Lint 规则
├── build.yaml                         # build_runner 配置
├── .env.example
└── TEST_CASES.md
```

### 1.2 目录规则

| 规则 | 说明 |
|------|------|
| features/ 按功能拆分 | 每个功能自包含 data/domain/presentation，不跨功能引用 data/ |
| core/ 禁止业务逻辑 | 只放基础设施（网络、存储、主题、工具） |
| shared/ 放跨功能共享 | 两个以上 feature 共用的 provider/widget/model |
| domain/ 可选 | 简单 CRUD 场景可省略 domain/，直接 DTO 传递 |
| 一个文件一个公开类 | 文件名与主要类名对应（snake_case） |

### 1.3 入口文件

```dart
// main.dart
void main() {
  runApp(const ProviderScope(child: App()));
}

// app.dart
class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      routerConfig: router,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
    );
  }
}
```

---

## 二、Riverpod 状态管理

### 2.1 Provider 类型选择

使用 `riverpod_generator`（@riverpod 注解）自动生成 Provider，禁止手写 Provider 声明。

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^2.6.0
  riverpod_annotation: ^2.6.0

dev_dependencies:
  riverpod_generator: ^2.6.0
  build_runner: ^2.4.0
```

**类型选择规则：**

| 场景 | 用法 | 示例 |
|------|------|------|
| 同步计算/常量 | `@riverpod` 函数 | 主题、配置、计算值 |
| 异步一次性获取 | `@riverpod` async 函数 | 获取用户详情 |
| 带参数的查询 | `@riverpod` 函数 + 参数 | 按 ID 获取数据 |
| 可变状态（同步） | `@riverpod` class extends _$Xxx | 表单状态、开关 |
| 可变状态（异步） | `@riverpod` class + AsyncValue | 列表 CRUD、分页 |
| 全局长驻 | `@Riverpod(keepAlive: true)` | 认证状态、Dio 实例 |

### 2.2 代码生成模式

```dart
// 推荐：使用 @riverpod 注解（自动生成 Provider）
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'user_provider.g.dart';

// 只读 Provider（函数式）
@riverpod
Future<User> userDetail(Ref ref, {required int userId}) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/users/$userId');
  return User.fromJson(response.data);
}

// 可变状态 Provider（类式）
@riverpod
class UserList extends _$UserList {
  @override
  Future<List<User>> build() async {
    final dio = ref.watch(dioProvider);
    final response = await dio.get('/api/users');
    return (response.data['items'] as List).map((e) => User.fromJson(e)).toList();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => build());
  }

  Future<void> deleteUser(int id) async {
    final dio = ref.read(dioProvider);
    await dio.delete('/api/users/$id');
    ref.invalidateSelf();  // 重新获取列表
  }
}

// 全局长驻 Provider
@Riverpod(keepAlive: true)
class Auth extends _$Auth {
  @override
  AuthState build() {
    return const AuthState.unauthenticated();
  }

  Future<void> login(String username, String password) async { ... }
  void logout() { ... }
}
```

### 2.3 ref 使用规则

| 方法 | 用途 | 使用场景 |
|------|------|---------|
| `ref.watch(provider)` | 响应式监听，值变化时重建 | build() 方法中 |
| `ref.read(provider)` | 一次性读取，不监听变化 | 事件处理（onPressed、onSubmit） |
| `ref.listen(provider, callback)` | 监听变化执行副作用 | 显示 SnackBar、导航 |
| `ref.invalidate(provider)` | 强制刷新 Provider | 数据变更后刷新列表 |

**禁止：**
- 禁止在 `build()` 中用 `ref.read()`（应该用 `ref.watch()`）
- 禁止在 `onPressed` 回调中用 `ref.watch()`（应该用 `ref.read()`）

### 2.4 Widget 选择

```dart
// ConsumerWidget — 无状态，优先使用
class UserListPage extends ConsumerWidget {
  const UserListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final users = ref.watch(userListProvider);
    return users.when(
      data: (list) => ListView(...),
      loading: () => const CircularProgressIndicator(),
      error: (err, stack) => ErrorView(error: err),
    );
  }
}

// ConsumerStatefulWidget — 需要 initState/dispose 或动画控制器时使用
class AnimatedPage extends ConsumerStatefulWidget { ... }
```

**选择规则：** 优先 `ConsumerWidget`，只有需要 `StatefulWidget` 生命周期时才用 `ConsumerStatefulWidget`。

### 2.5 禁止事项

| 禁止 | 说明 |
|------|------|
| `StateNotifier` / `StateNotifierProvider` | 已废弃，使用 `Notifier` / `AsyncNotifier` |
| `ChangeNotifier` / `ChangeNotifierProvider` | Riverpod 不推荐，使用 Notifier |
| 手写 Provider 声明 | 必须用 `@riverpod` 注解 + code generation |
| `ref.watch()` 在事件回调中 | 事件回调用 `ref.read()` |
| Provider 间循环依赖 | 重新设计数据流方向 |

---

## 三、命名规范

### 3.1 文件命名

全部 `snake_case`，文件名反映内容：

```
user_profile_page.dart       # 页面
user_list_provider.dart      # Provider
auth_repository.dart         # Repository
user_entity.dart             # 实体
user_dto.dart                # DTO
dio_client.dart              # 工具类
login_form.dart              # Widget
token_interceptor.dart       # 拦截器
```

### 3.2 类命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Page | `{Feature}{Action}Page` | `UserListPage`, `LoginPage` |
| Widget | 描述性 PascalCase | `LoginForm`, `UserCard`, `ErrorView` |
| Provider (函数式) | `{entity}{action}Provider` (自动生成) | `userDetailProvider`, `userListProvider` |
| Provider (类式) | `{Entity}{Action}` + `Provider` (自动生成) | `UserList` → `userListProvider` |
| Notifier | `{Entity}{Action}` | `UserList`, `Auth`, `ThemeMode` |
| Repository | `{Feature}Repository` | `AuthRepository`, `UserRepository` |
| Entity | `{Name}` | `User`, `Order`, `Factor` |
| DTO | `{Name}Dto` 或 `{Name}Response` | `UserDto`, `LoginResponse` |
| Service | `{Feature}Service` | `OssService`, `NotificationService` |

### 3.3 变量和函数命名

```dart
// 变量：camelCase
final userName = 'John';
final isLoading = false;
final userList = <User>[];

// 函数：camelCase，动词开头
Future<User> fetchUser(int id) async { ... }
void deleteUser(int id) { ... }
bool isValidEmail(String email) { ... }

// 常量：lowerCamelCase（Dart 官方风格，不用 UPPER_SNAKE）
const defaultPageSize = 20;
const maxRetryCount = 3;

// 私有成员：_前缀
final _cache = <String, dynamic>{};
void _handleError(Object error) { ... }
```

### 3.4 目录和包命名

```
features/user_management/     # snake_case
core/network/                 # snake_case
shared/widgets/               # snake_case
```

---

## 四、网络层（Dio）

### 4.1 Dio 实例封装

```dart
// core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'dio_client.g.dart';

@Riverpod(keepAlive: true)
Dio dio(Ref ref) {
  final env = ref.watch(envProvider);
  final dio = Dio(BaseOptions(
    baseUrl: env.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));

  dio.interceptors.addAll([
    TokenInterceptor(ref),
    RefreshInterceptor(ref),
    UnwrapInterceptor(),
    ErrorInterceptor(ref),
  ]);

  return dio;
}
```

### 4.2 拦截器

**Token 注入：**
```dart
class TokenInterceptor extends Interceptor {
  final Ref ref;
  TokenInterceptor(this.ref);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await TokenStorage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}
```

**响应解包（对齐 eapi 格式）：**
```dart
class UnwrapInterceptor extends Interceptor {
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final data = response.data;
    if (data is Map && data.containsKey('code') && data.containsKey('data')) {
      // eapi 格式: {code: 200, message: "success", data: {...}}
      response.data = data['data'];
    }
    handler.next(response);
  }
}
```

**401 Token 刷新（使用 QueuedInterceptor 防止竞态）：**

> **关键：** 使用 `QueuedInterceptor` 而非 `Interceptor`。QueuedInterceptor 串行处理请求，
> 刷新期间后续 401 请求自动排队等待，无需手动管理队列。
> 刷新 token 必须用**独立 Dio 实例**，避免被自身拦截器死锁。

```dart
class RefreshInterceptor extends QueuedInterceptor {
  final Ref ref;
  final Dio _refreshDio = Dio();  // 独立实例，不经过拦截器链

  RefreshInterceptor(this.ref);

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    try {
      final refreshToken = await TokenStorage.getRefreshToken();
      if (refreshToken == null) {
        ref.read(authProvider.notifier).logout();
        return handler.next(err);
      }

      // 用独立 Dio 实例刷新 token
      final response = await _refreshDio.post(
        '${ref.read(envProvider).apiBaseUrl}/api/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newToken = response.data['data']['access_token'];
      await TokenStorage.saveAccessToken(newToken);

      // 用新 token 重试原请求
      err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
      final retryResponse = await ref.read(dioProvider).fetch(err.requestOptions);
      handler.resolve(retryResponse);
    } catch (e) {
      // 刷新失败 → 登出
      ref.read(authProvider.notifier).logout();
      handler.next(err);
    }
  }
}
```

### 4.3 Repository 模式

```dart
// features/user/data/user_repository.dart
class UserRepository {
  final Dio _dio;
  UserRepository(this._dio);

  Future<List<User>> getUsers({int page = 1, int pageSize = 20}) async {
    final response = await _dio.get('/api/users', queryParameters: {
      'page': page,
      'page_size': pageSize,
    });
    final data = response.data as Map<String, dynamic>;
    return (data['items'] as List).map((e) => User.fromJson(e)).toList();
  }

  Future<User> getUser(int id) async {
    final response = await _dio.get('/api/users/$id');
    return User.fromJson(response.data);
  }

  Future<void> deleteUser(int id) async {
    await _dio.delete('/api/users/$id');
  }
}

// Provider 注入 Repository
@riverpod
UserRepository userRepository(Ref ref) {
  return UserRepository(ref.watch(dioProvider));
}
```

### 4.4 禁止事项

- 禁止 `http.get()` / `HttpClient` / 裸 `Dio()` 不加拦截器
- 禁止在 Widget 中直接调用 Dio（通过 Provider + Repository）
- 禁止硬编码 API 地址（走环境配置）

---

## 五、路由（GoRouter）

### 5.1 路由定义

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

### 5.2 导航

```dart
// 声明式导航
context.go('/users');            // 替换当前页面栈
context.push('/users/123');      // 压入新页面
context.pop();                   // 返回

// 禁止使用 Navigator.push / Navigator.pushNamed
```

### 5.3 底部导航（StatefulShellRoute）

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

### 5.4 路由规则

| 规则 | 说明 |
|------|------|
| 全部用 GoRouter | 禁止 `Navigator.push` / `Navigator.pushNamed` |
| 认证守卫在 redirect 中 | 不在每个页面单独检查 |
| 路径参数用 `:id` | `/users/:id`，通过 `state.pathParameters['id']` 获取 |
| 查询参数用 `state.uri.queryParameters` | 分页、筛选等 |

---

## 六、数据模型与序列化

### 6.1 freezed + json_serializable

```yaml
# pubspec.yaml
dependencies:
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0

dev_dependencies:
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  build_runner: ^2.4.0
```

```dart
// features/user/domain/user_entity.dart
import 'package:freezed_annotation/freezed_annotation.dart';
part 'user_entity.freezed.dart';
part 'user_entity.g.dart';

@freezed
class User with _$User {
  const factory User({
    required int id,
    required String username,
    required String role,
    @JsonKey(name: 'is_active') required bool isActive,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

### 6.2 规则

| 规则 | 说明 |
|------|------|
| 数据模型用 `@freezed` | 不手写 `fromJson/toJson/copyWith/==` |
| 后端字段 snake_case → 前端 camelCase | 用 `@JsonKey(name: 'snake_case')` 映射 |
| 禁止手写序列化 | 必须用 json_serializable 代码生成 |
| 运行代码生成 | `dart run build_runner build --delete-conflicting-outputs` |

---

## 七、测试规范

### 7.1 测试分类

| 类型 | 位置 | 工具 | 重点 |
|------|------|------|------|
| Unit Test | `test/features/{name}/` | flutter_test + mocktail | Repository、Service、工具函数 |
| Provider Test | `test/features/{name}/` | flutter_test + ProviderContainer | Provider 状态变化 |
| Widget Test | `test/features/{name}/` | flutter_test + ProviderScope.overrides | 页面渲染和交互 |

### 7.2 Provider 测试

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class MockUserRepository extends Mock implements UserRepository {}

void main() {
  late MockUserRepository mockRepo;
  late ProviderContainer container;

  setUp(() {
    mockRepo = MockUserRepository();
    container = ProviderContainer(overrides: [
      userRepositoryProvider.overrideWithValue(mockRepo),
    ]);
  });

  tearDown(() => container.dispose());

  test('userList 初始化时获取用户列表', () async {
    when(() => mockRepo.getUsers()).thenAnswer(
      (_) async => [User(id: 1, username: 'test', role: 'admin', isActive: true, createdAt: DateTime.now())],
    );

    // 读取 provider 触发初始化
    final future = container.read(userListProvider.future);
    final users = await future;

    expect(users, hasLength(1));
    expect(users.first.username, 'test');
  });
}
```

### 7.3 Widget 测试

```dart
testWidgets('登录页面渲染正确', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(() => MockAuth()),
      ],
      child: const MaterialApp(home: LoginPage()),
    ),
  );

  expect(find.byType(TextFormField), findsNWidgets(2));
  expect(find.text('登录'), findsOneWidget);
});
```

### 7.4 Mock 工具

统一使用 `mocktail`（不是 mockito）：

```yaml
dev_dependencies:
  mocktail: ^1.0.0
```

```dart
class MockDio extends Mock implements Dio {}
class MockAuthRepository extends Mock implements AuthRepository {}
```

### 7.5 测试规则

| 规则 | 说明 |
|------|------|
| 每个 feature 有对应测试目录 | `test/features/{name}/` |
| Repository 和 Provider 必须测试 | 业务逻辑的核心 |
| Mock 用 mocktail | 禁止 mockito（mocktail 无需 codegen） |
| 遵循项目 TDD 流程 | 先写测试 → 再实现 → 回归 |

---

## 八、Dart 语言规范

### 8.1 类型标注

```dart
// 显式标注公开 API 的返回类型
Future<List<User>> fetchUsers() async { ... }
String formatDate(DateTime date) { ... }

// 局部变量可用 final/var 推断
final users = await fetchUsers();
var count = 0;

// 禁止 dynamic（除非与原生 JSON 交互的边界点）
```

### 8.2 Null Safety

```dart
// 优先用非空类型
String name = 'default';       // 非空

// 只在真正可能为 null 时用 ?
String? middleName;

// 禁止滥用 !（bang operator），先 null check
if (user != null) {
  print(user.name);            // 安全
}
// 或用 ?.
user?.name;

// 禁止
print(user!.name);             // 可能运行时崩溃
```

### 8.3 异步

```dart
// async/await 优先
final user = await fetchUser(id);

// 多个独立异步操作用 Future.wait 并行
final (users, orders) = await (
  fetchUsers(),
  fetchOrders(),
).wait;

// 禁止 .then() 链式调用（可读性差）
// fetchUser(id).then((user) => fetchOrders(user.id)).then(...)  // 禁止
```

### 8.4 集合操作

```dart
// 推荐：collection-if / collection-for
final widgets = [
  const Header(),
  if (showBanner) const Banner(),
  for (final item in items) ItemCard(item: item),
];

// 推荐：级联操作符
final paint = Paint()
  ..color = Colors.blue
  ..strokeWidth = 2.0;
```

### 8.5 构造函数

```dart
// 推荐：命名参数 + required
class UserCard extends StatelessWidget {
  const UserCard({
    super.key,
    required this.user,
    this.onTap,
  });

  final User user;
  final VoidCallback? onTap;
}

// 禁止位置参数超过 2 个
```

---

## 九、Lint 规则

### 9.1 analysis_options.yaml

```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - prefer_const_constructors
    - prefer_const_declarations
    - prefer_final_locals
    - avoid_print               # 禁止 print
    - require_trailing_commas   # 尾逗号（方便 diff）
    - sort_constructors_first
    - prefer_single_quotes      # 统一单引号
    - always_use_package_imports # 禁止相对导入

analyzer:
  errors:
    missing_return: error
    dead_code: warning
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
```

### 9.2 Import 规则

```dart
// 使用 package import（禁止相对导入）
import 'package:my_app/features/auth/data/auth_repository.dart';  // 正确
// import '../data/auth_repository.dart';                          // 禁止

// 导入顺序（dart > package > 项目 > 相对路径）
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:my_app/core/network/dio_client.dart';
import 'package:my_app/features/auth/data/auth_repository.dart';
```

---

## 十、代码自检清单

提交前逐条确认：

- [ ] 文件名全部 snake_case
- [ ] 公开类/函数有类型标注
- [ ] Provider 用 @riverpod 注解生成，不手写
- [ ] 无 StateNotifier / ChangeNotifier
- [ ] ref.watch 只在 build() 中，ref.read 只在事件回调中
- [ ] 路由全部用 GoRouter，无 Navigator.push
- [ ] 数据模型用 @freezed，无手写 fromJson
- [ ] HTTP 请求通过 DioClient，无裸 http.get / Dio()
- [ ] 无 print()，调试用 debugPrint 或 logger
- [ ] 无 dynamic 类型（JSON 边界除外）
- [ ] 无 ! bang operator（先 null check）
- [ ] 常量构造函数加 const
- [ ] 尾逗号（trailing comma）
- [ ] package import，无相对导入
- [ ] 代码生成文件已更新（`dart run build_runner build`）
- [ ] 新增功能有对应测试
- [ ] TEST_CASES.md 已同步
