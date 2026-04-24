---
description: Flutter Dio 网络层 + 拦截器 + 错误处理
paths:
  - "**/core/network/**/*.dart"
  - "**/dio_client.dart"
  - "**/interceptors/**/*.dart"
  - "**/network/**/*.dart"
---

# Flutter 网络层规范

## 一、网络层（Dio）

### 1.1 Dio 实例封装

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

### 1.2 拦截器

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
      // eapi 格式: {code: "SUCCESS", message: "success", data: {...}, timestamp: ...}
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

### 1.3 Repository 模式

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

### 1.4 禁止事项

- 禁止 `http.get()` / `HttpClient` / 裸 `Dio()` 不加拦截器
- 禁止在 Widget 中直接调用 Dio（通过 Provider + Repository）
- 禁止硬编码 API 地址（走环境配置）

---

## 二、错误处理（Flutter）

Dio interceptor 统一处理，模式与前端对齐：

```dart
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.response?.statusCode) {
      case 401: // → 跳转登录
      case 403: // → 提示无权限
      case 422: // → 提取 message 显示
    }
    handler.next(err);
  }
}
```

---

## 三、网络层规范（跨端对齐）

### 3.1 Flutter 唯一方式

**唯一方式：** Dio + 拦截器，封装与 ekit request 对齐。

```dart
// core/network/dio_client.dart
class DioClient {
  late final Dio _dio;

  DioClient({required String baseUrl}) {
    _dio = Dio(BaseOptions(baseUrl: baseUrl))
      ..interceptors.addAll([
        TokenInterceptor(),    // 注入 Authorization header
        RefreshInterceptor(),  // 401 自动刷新
        UnwrapInterceptor(),   // 解包 {code, data, message} → data
        ErrorInterceptor(),    // 统一错误处理
      ]);
  }
}
```

**禁止：** `http.get()`、`HttpClient`、裸 `Dio()` 不加拦截器

### 3.2 响应解包

前端和 Flutter 的解包逻辑必须与后端 eapi response 格式对齐：

```
后端返回: { code: "SUCCESS", message: "success", data: {...}, timestamp: ... }
                                                      ↓ unwrap
前端/Flutter 拿到: {...}  (直接是 data 的内容)
```

分页响应解包后拿到 `{ items, total, page, page_size }`（保持 snake_case 对齐后端 JSON）。
