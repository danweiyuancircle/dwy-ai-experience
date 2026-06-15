---
description: Flutter / Dart 测试规范(mocktail + ProviderContainer + Widget 测试)
paths:
  - "**/test/**/*.dart"
  - "**/*_test.dart"
---

# Flutter 测试规范

## 一、测试分类

| 类型 | 位置 | 工具 | 重点 |
|------|------|------|------|
| Unit Test | `test/features/{name}/` | flutter_test + mocktail | Repository、Service、工具函数 |
| Provider Test | `test/features/{name}/` | flutter_test + ProviderContainer | Provider 状态变化 |
| Widget Test | `test/features/{name}/` | flutter_test + ProviderScope.overrides | 页面渲染和交互 |

## 二、Provider 测试

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

## 三、Widget 测试

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

## 四、Mock 工具

统一使用 `mocktail`（不是 mockito）：

```yaml
dev_dependencies:
  mocktail: ^1.0.0
```

```dart
class MockDio extends Mock implements Dio {}
class MockAuthRepository extends Mock implements AuthRepository {}
```

## 五、测试规则

| 规则 | 说明 |
|------|------|
| 每个 feature 有对应测试目录 | `test/features/{name}/` |
| Repository 和 Provider 必须测试 | 业务逻辑的核心 |
| Mock 用 mocktail | 禁止 mockito（mocktail 无需 codegen） |
| 遵循项目 TDD 流程 | 先写测试 → 再实现 → 回归 |
