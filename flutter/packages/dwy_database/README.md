# dwy_database

纯 Dart Foundation 包，面向 Android/iOS/桌面原生平台，通过 Drift + SQLite 管理资源；本实现导入 `dart:io`，不宣称支持 Web。

共享移动端项目基线为 **iOS 18+、Android 10+（minSdk 29）**。本包不伪造原生 OS 配置；SQLite 原生产物的最低版本与打包兼容性需统一构建验证，升级不得静默抬高基线。

`DwyDatabase.open` 创建宿主指定文件的父目录，使用 Drift 原生后台 isolate，完成产品迁移后才返回 owner。打开失败会等待资源清理；若清理也失败，`DwyDatabaseOpenFailure` 同时保留两项原因，不擦除数据库。没有降级删库重建。

宿主传入自己的 `GeneratedDatabase` factory，保留 Drift 的 typed query、DAO、transaction 和 query stream。库不提供万能 CRUD、产品表或隐式数据库单例。

```dart
import 'dart:io';
import 'package:dwy_database/dwy_database.dart';
import 'note_database.dart';

Future<void> runExample(File accountDatabaseFile) async {
  final owner = await DwyDatabase.open(
    file: accountDatabaseFile,
    create: (executor) => ExampleNoteDatabase(executor),
  );
  try {
    await owner.transaction((db) => db.addNote('A local note'));
    // 页面可订阅 owner.database.watchNotes()；上层负责取消订阅。
  } finally {
    await owner.close();
  }
}
```

`example/note_database.dart` 是产品侧 schema/DAO/迁移的最小示例，不是共享业务表。数据库路径和账号隔离由 Assembly 配置，路径应使用应用数据目录，不能放临时缓存中。每个 owner 只供创建它的 isolate 使用；关闭/切换账号前停止新操作，等待事务与订阅结束，再 await close。已捕获的底层 database 引用不能在 owner 生命周期结束后继续使用。

## 生成与验证

```bash
cd flutter/packages/dwy_database
dart run build_runner build
dart analyze
dart test
```

`example/note_database.g.dart` 由 Drift 生成，未手写或伪造。当前基线为 Flutter 3.50.0 / Dart 3.14.0；真实文件数据库测试已运行，具体证据见 `flutter/docs/foundation-3.50-validation.md`。

测试使用临时目录中的真实 SQLite 文件，覆盖重开持久化、事务回滚、流更新、v1→v2 保留记录和失败迁移不擦数据。不使用内存数据库冒充磁盘验收。SQLite 3.x native-assets 的构建 hook 可能获取原生 SQLite 产物；首次运行应按批准的工具/依赖范围执行并核对产物，不能把声明依赖当作原生打包通过。

## 依赖与许可

| 直接依赖 | 版本 | pub 首次发布时间 UTC | 许可 |
| --- | --- | --- | --- |
| drift | 2.35.3 | 2026-10-23T15:42:38.337543Z | MIT |
| sqlite3 | 3.8.0 | 2026-10-23T14:38:43.613381Z | MIT |

两者由 Simon Binder 维护，可商用，须保留版权和许可声明，并纳入消费应用隐私协议的第三方开源组件附录。SQLite 原生引擎自身许可与 Dart binding 的 MIT 分开核对。

- [Drift](https://pub.dev/packages/drift/versions/2.35.3)、[许可](https://pub.dev/packages/drift/versions/2.35.3/license)、[源码](https://github.com/simolus3/drift)。
- [sqlite3](https://pub.dev/packages/sqlite3/versions/3.8.0)、[许可](https://pub.dev/packages/sqlite3/versions/3.8.0/license)、[源码](https://github.com/simolus3/sqlite3.dart)。

生成工具仅用于开发：drift_dev 2.35.3、build_runner 2.17.1；工作区单测 test 1.32.0 与 Flutter 3.50.0 的测试依赖对齐。版本调整原因见 `flutter/docs/flutter-3.50-migration.md`；依赖解析不代表原生移动端打包已通过。
