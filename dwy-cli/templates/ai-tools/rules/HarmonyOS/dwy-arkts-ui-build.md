---
description: HarmonyOS ArkUI 组件层 / V2 状态管理 / 图标资源 / 工程构建 / 运行时容错避坑（与 dwy-arkts-strict.md 语言层配套）
paths:
  - "**/*.ets"
  - "**/build-profile.json5"
  - "**/main_pages.json"
---

# ArkUI / 工程 / 运行时 避坑

`dwy-arkts-strict.md` 管语言语法层；本文件管 **ArkUI 组件、V2 状态管理、资源（图标）、工程构建、运行时容错**。
均为真机/DevEco 构建实测踩坑（编译期或运行期暴露，命令行 tsc 查不出）。

## 1. sys.symbol 图标名 ≠ SF Symbols 名，必须查鸿蒙清单逐个映射

iOS 用 SF Symbols（`tv.and.mediabox`），鸿蒙 `$r('sys.symbol.xxx')` 是**另一套命名体系**，
大量 SF 名在鸿蒙不存在，写错报 `Unknown resource name 'xxx'`。

- **权威清单**：`<DevEco-SDK>/openharmony/toolchains/id_defined.json`（约 4000+ 个，`type=symbol`），
  python 提取后 grep 验证目标名是否存在。
- **`$r('sys.symbol.x')` 的 x 必须是字面量**，不能用变量动态拼 → 只能逐处改，不能写映射函数。
- **常见映射**（SF → 鸿蒙）：

  | SF Symbols | 鸿蒙 sys.symbol |
  |---|---|
  | tv / tv.and.mediabox | `TV_tv` |
  | iphone / ipad | `phone` / `pad` |
  | command | `keyboard` |
  | cpu / memorychip | `memory_module` |
  | terminal | `code` |
  | pencil | `doc_plaintext_and_pencil` |
  | globe | `globe_and_keyboard` |
  | tag | `label` |
  | square.and.arrow.up | `share` |
  | checkmark.seal.fill | `checkmark_circle_fill` |
  | stop.fill | `stop_circle_fill` |
  | shippingbox | `card_package` |
  | square.stack.3d.up | `AI_square_stack` |
  | gearshape.fill / house / chevron.left | 同名（`gearshape_fill` / `house` / `chevron_left`，少数直通） |

  写前先 `grep -ix '<候选名>' id_defined.txt` 确认存在，别想当然。

## 2. 自定义组件后不能直接链通用属性（margin/layoutWeight/width…）

自定义 `@Component`/`@ComponentV2`（尤其带尾随 `@BuilderParam` 闭包的）**后面直接链通用属性
会编译失败**：`Declaration or statement expected` + `Cannot find name 'margin'`。

```typescript
// 错：HoldRepeatButton 是自定义组件，后链 .margin 解析失败
HoldRepeatButton({ action: f }) { this.icon() }
  .margin({ bottom: 184 })

// 对：外层包系统组件（Column/Row/Stack）再链
Column() {
  HoldRepeatButton({ action: f }) { this.icon() }
}.margin({ bottom: 184 })
```

需要偏移/尺寸时，要么外层包系统容器，要么给自定义组件加 `@Param` 参数在其内部应用。

## 3. 支持本地初始化的组件属性必须有默认值（mandatory-default-value-for-local-initialization）

DevEco **预览器/linter（PreviewBuild）比 assembleHap 更严**，会查这条；assembleHap 不查。

- **`@BuilderParam`** 必须给默认值（默认值是一个全局 `@Builder` 函数）：

  ```typescript
  @Builder function emptyContent(): void {}
  @ComponentV2
  struct Foo {
    @BuilderParam content: () => void = emptyContent;   // 不能写 `: () => void;`
  }
  ```

- **`@CustomDialog` 的 `controller`** 必须可选（否则同报无默认值）：

  ```typescript
  @CustomDialog
  struct MyDialog {
    controller?: CustomDialogController;   // 不能写 `controller: CustomDialogController;`
  }
  ```
  改可选后调用处要用可选链：`this.controller?.close()`（否则 `Object is possibly undefined`）。

- **例外**：`@Require @Param x: T;` 不受此规则约束（`@Require` 表必传，无需默认值）。

## 4. @ComponentV2 外部传入的回调属性必须用 @Param

父组件给子组件传属性（含回调）时，子组件该属性必须 `@Param` 装饰，否则报
`The 'regular' property 'xxx' cannot be initialized here (forbidden to specify)`：

```typescript
// 错：onDone 是普通属性，父层 Foo({ onDone: ... }) 传不进
struct Foo { onDone: () => void = () => {}; }
// 对
struct Foo { @Param onDone: () => void = () => {}; }
```

## 5. async 状态供 UI 同步读：用 @Trace 快照，别在 build 里 await

`build()` 是同步的，UI 不能 `await` 一个 async 方法拿状态（`Property 'kind' does not exist on
type 'Promise<T>'`）。把异步数据在装配/事件时算好，存进 `@Trace` 快照，UI 同步读快照：

```typescript
@ObservedV2 class Store {
  @Trace snapshot: State = defaultState;          // UI 读这个
  private cache = 0;
  async start(ctx): Promise<void> {
    this.cache = await this.loadFromAsset(ctx);    // 异步读一次缓存
    this.refresh();                                // 用缓存同步算快照
  }
  private refresh(): void { this.snapshot = compute(this.cache, Date.now()); }
}
```

## 6. 跨模块 import 必须从「声明源」取，不能经中转模块隐式重导出

ArkTS 不支持 TS 的「A 从 B import 某类型，C 再从 A import 同名」隐式重导出：
`Module '"../X"' declares 'Y' locally, but it is not exported`。**直接从声明 Y 的那个文件 import**。

```typescript
// 错：AdbTransport 只是 import 了 AdbLog（没 re-export），别处从 AdbTransport 取 AdbLog
import { AdbLog } from '../adb/AdbTransport';
// 对：从声明 AdbLog 的源文件取
import { AdbLog } from '../adb/AdbConnection';
```

## 7. 工程/资源杂项

- **`Stack` 居中用 `.alignContent(Alignment.X)`**，不是构造参数 `Stack({ alignment: X })`
  （`'alignment' does not exist in type 'StackOptions'`）。
- **`SymbolGlyph` 没有 `.textAlign`**：居中靠外层容器的 `justifyContent`/`alignItems`，别链 textAlign。
- **`build-profile.json5`（entry 模块）顶层字段固定**：apiType/targets/buildOption/buildOptionSet/
  buildModeBinder/entryModules/apiType 等。塞 `testOption` 之类非法字段报
  `Schema validate failed`。hypium 测试靠 `src/ohosTest/` 目录约定，不需在 build-profile 配。
- **退役/不编译的代码移出 `entry/src/main/ets`**（如 spike）：放在 ets 下仍会被编译。
  移到工程根的 `_archive/` 之类，并从 `main_pages.json` 去掉。

## 8. 运行时：全局状态装配（bootstrap）必须分步容错，不能全有或全无

app 入口的「装配全局状态」若把多个步骤串成一个 `await` 链，**任一步抛异常（尤其模拟器/无账号
环境下的 IAP、首次无持久化）会让后面全不执行**，导致全局 router/store 为 null，UI 一进就崩
（`AppContext 未装配` / `Object is possibly undefined`）。

```typescript
// 错：IAP 在模拟器抛错（如华为 IAP 错误码 27656204）→ router 没装配 → 全崩
async bootstrap(ctx) {
  await store.load(ctx);
  await iap.start(ctx);          // ← 模拟器抛错，下面不执行
  this.router = new Router(...); // ← 永远到不了
}

// 对：每步独立容错，核心对象（router）一定装配成功
async bootstrap(ctx) {
  await this.safe('存档', () => store.load(ctx));
  await this.safe('内购', () => iap.start(ctx));   // 失败只 log，降级
  this.router = new Router(...);                    // 一定执行
}
private async safe(name, step) {
  try { await step(); } catch (e) { console.error(`[${name}]降级: ${(e as Error).message}`); }
}
```

模块内部同理：**核心数据（如试用锚点）与非关键外部依赖（如 IAP 查询）分开 try**，
非关键失败不连累核心，给 UI 一个合理降级默认值。

## 9. DevEco 命令行构建（绕开 IDE，拿带 File:行:列 的错误）

```bash
NODE=/Applications/DevEco-Studio.app/Contents/tools/node/bin/node
HVIGOR=/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin/hvigorw.js
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk   # 停 daemon 后必设

# 配置校验
$NODE $HVIGOR --sync -p product=default --daemon
# 编译 + 打 HAP（验 ArkTS 编译；产物 entry/build/.../entry-default-unsigned.hap）
$NODE $HVIGOR assembleHap -p product=default --mode module -p module=entry@default --daemon \
  2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep "Error Message:"
# 预览器构建（linter 更严，查 @BuilderParam/controller 默认值等；用独立 .preview 缓存）
$NODE $HVIGOR --mode module -p module=entry@default -p product=default -p pageType=page \
  -p previewMode=true -p buildRoot=.preview PreviewBuild --daemon
```

- **必须 `--daemon`**：DevEco daemon 自动注入 SDK 路径；`--no-daemon` 报 `Invalid DEVECO_SDK_HOME`。
- **`Error Message:` 才是阻断错误**；`WARN ... may throw exceptions` 是建议，不阻断。
- **PreviewBuild 用独立 `.preview` 缓存**：改了源码仍报已修错误 → `rm -rf entry/.preview` 重跑。
- 两种构建都要过：assembleHap（真机包）+ PreviewBuild（linter 严，预览器）。

## 10. 仍需真机确认的（编译/预览过 ≠ 运行对）

见 `dwy-arkts-strict.md` 第 9 条（cryptoFramework 签名规格 / 公钥 DER 格式 / TCPSocket 局域网）。
补充：手撸 HTTP/2 的 HPACK 全字面量是否被对端（如 grpc-netty）接受、华为 IAP 需 AGC 后台
配商品 + 真机华为账号、asset/Preferences 在不同设备的可用性，均真机才能定论。
