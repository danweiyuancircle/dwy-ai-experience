---
description: Flutter + Dart 基础风格(结构/Riverpod/命名/模型/Dart 语言/Lint)
paths:
  - "**/*.dart"
  - "**/pubspec.yaml"
  - "**/analysis_options.yaml"
---

# Flutter + Dart 基础风格规范

## 全面屏 / 刘海屏适配

- Flutter 应用默认按 iOS 与 Android 全面屏、刘海屏、挖孔屏适配实现,不要依赖固定上下左右边距硬编码页面内容区。
- 优先使用 `SafeArea`、`MediaQuery.padding`、`MediaQuery.viewPadding`、`MediaQuery.viewInsets` 与响应式布局约束处理状态栏、底部手势区、键盘遮挡。
- 页面主体、底部操作栏、表单输入区、弹层内容必须显式处理安全区域,避免被刘海、Home Indicator、导航栏或软键盘遮挡。
- 全屏背景、沉浸式插画、遮罩层可以铺满屏幕,但前景可交互内容默认留在安全区域内。
- 禁止写死 iOS 状态栏高度、Android 导航栏高度或机型刘海尺寸,统一通过系统安全区域与 inset 信息计算。

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

### 3.4 禁止魔法字符串

同一个字符串字面量在文件内出现 2 次及以上时，**必须**提取为常量。

```dart
// ❌ 魔法字符串散落多处
await secureStorage.write(key: 'access_token', value: token);
final t = await secureStorage.read(key: 'access_token');

// ✅ 提取为常量
const _accessTokenKey = 'access_token';
await secureStorage.write(key: _accessTokenKey, value: token);
final t = await secureStorage.read(key: _accessTokenKey);

// ✅ 跨文件共享的 key 放到常量文件
// core/constants/storage_keys.dart
class StorageKeys {
  StorageKeys._();
  static const accessToken = 'access_token';
  static const refreshToken = 'refresh_token';
  static const theme = 'theme';
}
```

### 3.5 目录和包命名

```
features/user_management/     # snake_case
core/network/                 # snake_case
shared/widgets/               # snake_case
```

---

## 四、数据模型与序列化

### 4.1 freezed + json_serializable

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

### 4.2 规则

| 规则 | 说明 |
|------|------|
| 数据模型用 `@freezed` | 不手写 `fromJson/toJson/copyWith/==` |
| 后端字段 snake_case → 前端 camelCase | 用 `@JsonKey(name: 'snake_case')` 映射 |
| 禁止手写序列化 | 必须用 json_serializable 代码生成 |
| 运行代码生成 | `dart run build_runner build --delete-conflicting-outputs` |

---

## 五、Dart 语言规范

### 5.1 类型标注

```dart
// 显式标注公开 API 的返回类型
Future<List<User>> fetchUsers() async { ... }
String formatDate(DateTime date) { ... }

// 局部变量可用 final/var 推断
final users = await fetchUsers();
var count = 0;

// 禁止 dynamic（除非与原生 JSON 交互的边界点）
```

### 5.2 Null Safety

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

### 5.3 异步

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

### 5.4 集合操作

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

### 5.5 构造函数

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

## 六、Lint 规则

### 6.1 analysis_options.yaml

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

### 6.2 Import 规则

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

## 七、代码自检清单

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

---

## 八、环境变量管理（Flutter）

使用编译时注入或 `.env` + `flutter_dotenv`：

```bash
# .env
API_BASE_URL=http://localhost:8000/api

# 或编译时注入
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api
```

**强制规则：**

| 规则 | 说明 |
|------|------|
| 每个项目必须有 `.env.example` | 列出所有变量名 + 注释说明，值用占位符 |
| `.env` 文件禁止提交 git | 已在 git-security.md 约束 |
| 禁止硬编码 | 数据库连接、密钥、API 地址等必须走环境变量 |

---

## 九、状态管理（跨端共识）

| 平台 | 方案 | 详细规范 |
|------|------|---------|
| Vue | Pinia Setup Store | 见 `vue-code-style.md` 状态管理章节 |
| Flutter | Riverpod | 见本文件第二章 |

**跨端共识：**
- 认证状态全局管理（Vue: `useAuthStore`，Flutter: `authProvider`）
- 页面级状态就近管理，不上提到全局
- 缓存策略：列表数据按需刷新，不做客户端持久化缓存（除离线场景）
