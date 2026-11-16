# dwy_network

基于 Dio 的纯 Dart 服务客户端，不依赖 Widget。每个服务创建独立实例，应用负责注入和关闭；不包含登录状态或固定后端响应格式。

```dart
import 'package:dwy_network/dwy_network.dart';

Future<void> main() async {
  final client = DwyHttpClient(DwyHttpConfig(
    baseUrl: Uri.parse('https://example.com/api/'),
  ));
  try {
    await client.request<Map<String, dynamic>>(
      'status',
      decode: (value) => value as Map<String, dynamic>,
    );
  } finally {
    await client.close();
  }
}
```

## 服务与安全边界

- 基础地址必须是 HTTP(S) 地址，不允许 URL 凭据、query 或 fragment。请求相对路径按照 `Uri.resolve` 解析；需要保留 `/api/` 前缀时，不以 `/` 开始请求路径。
- 普通 request/upload/download 拒绝其他 origin 的绝对地址，默认不跟随重定向，防止服务凭据误用于其他目标。
- 云端、局域网等不同服务使用独立实例，按需注入 headers，不使用全局 token。
- 默认无自动重试、无自动刷新 token、无业务 envelope 解包。产品 Repository 提供 `decode` 和业务规则。
- 只记录请求序号、方法、origin、状态及耗时，不记录路径、query、headers、请求/响应正文或原始异常。
- `DwyNetworkException` 暴露稳定失败分类和 HTTP 状态，保留 `cause` 与原始堆栈，`toString()` 不包含可能带凭据的 Dio 异常文本。产品可显式读取 `responseData` 解码 4xx/5xx 业务错误；禁止直接记录原始 payload/cause。
- decode 中的 FormatException/TypeError 转为协议错误；其他产品程序错误继续抛出，不无差别吞异常。
- 日志失败通过 `diagnosticFailures` 独立广播，保留 cause/stack，不会把成功的 POST 改成失败，也不会覆盖 HTTP 或取消错误。需要观察的宿主应在请求前订阅，关闭客户端前恢复或取消暂停的订阅。

## 取消、传输和生命周期

- `DwyRequestCancellation` 只取消引用该句柄的请求；下载和上传使用 Dio 的真实字节进度，未知 total 可能为 -1，不根据耗时伪造百分比。
- upload 使用 MultipartFile 流读取文件；宿主必须持有文件访问授权直到 Future 完成。
- `final file = await client.download('file', parent: downloadDirectory)` 在指定目录下分配独占子目录，返回其中的完整文件，不接受任意共享目标路径。这避免排他预留与 rename 之间的覆盖竞态；并发下载分配不同目录，调用期间宿主不能修改这些私有子目录。
- HTTP 失败或取消时清理本次子目录，正常返回才把文件所有权交给宿主。使用结束后宿主删除 `file.parent`；产品需要另存为用户路径时，由产品调用系统保存流程。
- 清理也失败时抛 `DwyDownloadCleanupFailure`，保留 operation、cleanup 和待清理 directory，不掩盖原始失败，不删除父目录中的其他文件。
- `close()` 拒绝新操作、请求取消并等待 DWY API 中已开始的操作结束。logger 由宿主持有，在所有客户端关闭之后关闭。
- `transport` 是高级 Dio escape hatch，用于自定义 adapter/interceptor/stream。直接使用会绕过 DWY origin 校验、生命周期和安全诊断，调用方显式承担这些职责。常规业务应使用 DWY API。

本包使用 `dart:io` 的文件 API，当前范围为 Dart VM 和 Flutter 移动端/桌面，不声明 Web 文件上传下载支持。
本轮统一移动端宿主基线为 iOS 18+、Android 10+（minSdk 29）；纯 Dart 包本身不设置或伪造平台部署配置。

## 验证

从 Flutter workspace 解析依赖后：

```bash
cd packages/dwy_network
dart test
dart analyze
```

测试使用本机 loopback HTTP server，不依赖业务服务。用例见 `test/TEST_CASES.md`；源码完成不代表运行通过。

## 依赖与许可

用户指定底座 **Dio 5.11.1**，pub registry 首次发布时间 **2026-09-04T02:46:21.721502Z**，超过 7 天。来源为 [pub registry](https://pub.dev/api/packages/dio/versions/5.11.1) 和 [cfug/dio](https://github.com/cfug/dio)。MIT，可商用，需保留版权和许可声明。消费产品附录使用实际 lockfile 版本。

另依赖 workspace `dwy_log`。测试约束与 Flutter SDK 测试依赖统一解析，不安装新 SDK 或工具。
