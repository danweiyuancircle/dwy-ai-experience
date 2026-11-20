# dwy_image

独立 Flutter 图片包，基于 `cached_network_image`，不依赖 `dwy_design`。统一资源、本地文件、内存和网络图片入口；主题从宿主读取，不复制一套颜色配置。

## 支持与状态

- 共享移动端约束：iOS 18+、Android 10+（API 29）。具体插件最低版本、原生构建和真机结果由工作区集成验证，当前没有通过这项验收。
- Dart `>=3.14.0 <4.0.0`，Flutter `>=3.50.0`；开发工具链固定版本见 `flutter/docs/development-baseline.md`。
- 本地文件入口不支持 Web。上游 Web 实现不提供与移动端相同的磁盘缓存，不把 Web Playground 当作移动端缓存证明。
- 当前只完成源码、测试源码与静态检查；尚未安装 SDK、解析依赖、运行测试或进行 GUI/真机验收。

## 使用

```dart
import 'package:dwy_image/dwy_image.dart';

final images = DwyImageCache(namespace: 'example_product_account_42');
final source = DwyImageSource.network(
  Uri.parse('https://images.example.com/avatar.png'),
  cache: images,
  headers: const {'Authorization': 'Bearer TOKEN_FROM_SESSION'},
);

final avatar = DwyImage(
  source: source,
  width: 64,
  height: 64,
  semanticLabel: '用户头像',
  loadingLabel: '正在加载头像',
  errorLabel: '头像暂不可用',
  retryLabel: '重试',
);
```

本地来源：`DwyImageSource.asset(name)`、`DwyImageSource.file(path)`、`DwyImageSource.memory(bytes)`。内存缓冲区在使用期间不得修改；临时文件必须保留到图片解码完成。

Widget 强制提供逻辑尺寸，加载/失败时布局不改变；按设备像素比生成解码上限，保持原始宽高比。`cacheWidth` / `cacheHeight` 是可选的物理像素上限，不是下载时压缩。没有创建额外的磁盘缩略版本，避免失效时残留未撤销的副本。

- `source.provider(cacheWidth: ..., cacheHeight: ...)`：接入头像、背景和 Flutter 其他组合控件。
- `await source.prefetch(context)`：预加载/解码；失败会返回给调用方，不吞掉错误。
- `await source.invalidate()`：网络图片移除本 scope 的原文件和已登记的所有解码尺寸。本地图片覆盖同一个 source 登记的尺寸。
- `await images.clear()`：只清当前命名空间的磁盘和已登记内存缓存。
- `await images.dispose()`：拒绝新读、等待正在进行的缓存流、关闭元数据仓库；不自动删除磁盘缓存。

默认错误 UI 提供可操作的重试按钮，不显示可能带 URI/认证信息的原始异常。`placeholderBuilder` 和 `errorBuilder` 允许应用覆盖；应用负责其文案和展示策略。减少动态效果开启时不播放淡入。

## 缓存所有权与隐私

1. 每个产品/账户使用独立、稳定、非秘密的 namespace。只允许字母、数字、下划线、连字符，长度 1–80；同一 isolate 只允许一个存活实例持有同名空间。
2. 不使用 Token 作为 namespace，不记录 Authorization。URL 应优先不携带凭据；上游 Flutter/Provider 的调试诊断可能包含原 URL，因此不要把原始异常/Provider 输出直接提交日志或用户界面。
3. 同一 URL 在不同 namespace 下具有不同内存缓存键。认证头自身不构成身份；切换用户或权限上下文时必须切换 namespace，不能复用同一个账户缓存。
4. 缓存不是加密存储。敏感内容是否允许落盘由应用决定；不适合落盘的私有图片不要走本缓存入口。
5. 注销时先移除消费者，并等待应用的预加载操作，再依次 `await images.clear()`、`await images.dispose()`。禁止在仍展示私有图片的页面上宣称已完成清理。
6. 清理会等待已开始的缓存流，以免后台下载在清空后重新落盘。上游缓存管理器没有公开的通用 HTTP 取消接口；网络响应迟迟不结束时清理会等待，不能把“发起清理”当作已经完成。
7. `custom` 构造器允许高级宿主/测试注入缓存仓库、文件系统和 FileService；这些必须属于本 namespace。`manager` 是高级缓存适配入口，不应从业务页面直接调用或另起未被管理的下载。

## 选型与精确版本

| 依赖 | 版本 | Registry 首次发布时间（UTC） | 许可 |
| --- | --- | --- | --- |
| cached_network_image | 4.0.6 | 2026-10-29 12:16:31.892001 | MIT |
| flutter_cache_manager | 3.5.0 | 2026-11-04 07:11:52.925282 | MIT |
| file（仅测试） | 7.0.1 | 2024-10-08 15:54:11.380188 | BSD-3-Clause |

前两者均为 Baseflow 维护，选型时正式版已发布满 7 天；未升级到 `4.0.7`。默认加载、错误重试和占位使用独立 `cupertino_ui`。缓存与图片来源仍使用现有上游实现。消费方可以用 `placeholderBuilder` 和 `errorBuilder` 提供自身样式。

来源：[精确图片包元数据](https://pub.dev/api/packages/cached_network_image/versions/4.0.6)、[缓存管理器元数据](https://pub.dev/api/packages/flutter_cache_manager/versions/3.5.0)、[图片包源码](https://github.com/Baseflow/flutter_cached_network_image)、[缓存管理器源码](https://github.com/Baseflow/flutter_cache_manager)。许可声明见 `THIRD_PARTY.md`；应用发布时把锁定版本与许可加入隐私协议的「第三方开源组件」附录。

## 验证

工作区主代理把本包加入 `flutter/pubspec.yaml` 后，在已批准并安装的 SDK 上执行：

```bash
cd flutter/packages/dwy_image
flutter analyze
flutter test
```

测试范围见 `TEST_CASES.md`。本包不修改 Playground；主代理将图片示例集成到现有展示应用。
