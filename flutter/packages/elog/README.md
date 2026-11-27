# dwy_log

纯 Dart 本机日志，应用注入专用目录，不依赖 Widget、Flutter Engine 或 `path_provider`。

```dart
import 'dart:io';
import 'package:dwy_log/dwy_log.dart';

Future<void> main() async {
  final directory = await Directory.systemTemp.createTemp('my-app-diagnostics-');
  final log = await DwyLogger.open(DwyLogConfig(
    directory: directory,
  ));
  try {
    await log.category('startup').info('Application started', fields: {'build': '1'});
    await log.flush();
  } finally {
    await log.close();
    await directory.delete(recursive: true);
  }
}
```

## 契约

- 同一个专用目录只能由一个 isolate 中的一个实例写入；多个 category 共享此实例。
- 日志方法返回 Future，调用方应 await 并处理文件系统错误。关闭后拒绝写入，重复关闭返回同一个结果。
- JSON Lines 格式；模块、级别、结构化字段一致。默认最低级别 info，不输出控制台、不上传。
- 字段名包含 token、password、secret、authorization、cookie、api key 等时隐藏值；可识别 URL 去除凭据、query 和 fragment。异常只记录类型，避免任意异常正文携带响应或凭据。
- 自由消息不可包含秘密或个人内容。脱敏针对明确的字段/常见凭据格式，不能代替调用方的数据最小化。
- `logger` 负责过滤及格式化；DWY 文件输出在同一异步队列串行完成写入、轮转、保留、flush、导出和关闭，不使用后台轮转定时器。
- 默认每个文件约 2 MiB、最多 5 个归档。新记录将超过阈值时先轮转；单条完整 JSON 记录可以超过阈值，不截断记录。
- 默认保留 7 天，过期归档在打开、轮转、显式 flush 和导出时清理。
- `flush()` 等待此前队列并刷新同一个文件句柄，不关闭重开 backend。写入、轮转或清理失败向当前调用者传出；会话随后拒绝新操作并以 `DwyLogUnavailable.cause` 保留根因，`close()` 仍尝试释放文件。
- 导出创建新的快照子目录，不覆盖文件、不自动分享。宿主负责分享与清理；通过实际路径解析拒绝日志目录内部、`..` 和符号链接别名。
- `DwyLogFileOperations` 是文件操作注入点，默认使用 Dart 文件 API；替代实现必须在 Future 完成前结束自己持有的工作。

## 文件输出边界

独立审查确认 `logger.AdvancedFileOutput` 的定时轮转不等待异步回调，可能在关闭后重新打开文件，且内部吞掉部分错误。为修复已证实的生命周期问题，此包使用受控文件输出，并保留成熟 logger 的过滤/打印协议。没有私自 fork 上游或增加依赖。关闭正常返回不是断电持久化或合规留存保证；专用目录的跨进程独占由宿主负责。

当前实现面向 Dart VM 与 Flutter iOS/Android/desktop；使用 `dart:io`，不声明 Web 文件落盘支持。
本轮统一移动端宿主基线为 iOS 18+、Android 10+（minSdk 29）；本包不包含平台部署配置。

## 验证

从 Flutter workspace 解析依赖后：

```bash
cd packages/elog
dart test
dart analyze
```

具体用例见 `test/TEST_CASES.md`。当前执行结果由集成报告记录，测试源码不代表通过。

## 依赖与许可

用户指定底座 `logger`，锁定 **2.8.0**，pub registry 首次发布时间 **2026-09-05T17:20:29.963495Z**，超过 7 天。来源为 [pub registry](https://pub.dev/api/packages/logger/versions/2.8.0) 和 [SourceHorizon/logger](https://github.com/SourceHorizon/logger/tree/v2.8.0)。MIT，可商用，需保留版权及许可文本。消费产品的第三方开源组件附录需列出实际 lockfile 版本。

测试版本与宿主 Flutter `flutter_test/test_api` 统一解析；运行时版本固定，不执行工具安装。
