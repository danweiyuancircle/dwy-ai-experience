---
description: HarmonyOS ArkUI 组件层 / V2 状态管理 / 图标资源 / 工程构建 / 运行时容错避坑（与 dwy-arkts-strict.md 语言层配套）
paths:
  - "**/*.ets"
  - "**/build-profile.json5"
  - "**/main_pages.json"
---

# ArkUI / 工程 / 运行时 避坑

| 文件 | 层 |
|---|---|
| `dwy-arkts-strict.md` | 语言语法（arkts-no-*） |
| **本文件** | 组件 API、V2 状态、资源、工程构建、设备/运行时 |
| `dwy-arkts-ui-design.md` | UI 设计与交互（弹层关闭、加载三态等事前约束） |
| `dwy-harmony-pitfalls.md` | 四栏踩坑归档 |

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

## 11. assembleHap 未配 signingConfigs → unsigned.hap

- **现象**：`hvigorw assembleHap` 成功但日志 `Will skip sign 'hos_hap'`，产物 `entry-default-unsigned.hap`；真机拒装。
- **根因**：`build-profile.json5` 的 `signingConfigs` 为空。
- **正确做法**：DevEco → Project Structure → Signing Configs 自动签名写回工程；**模拟器**可装 unsigned；**真机**必须签名。
- **适用**：CLI / CI 打包。

## 12. 本地模拟器（HVD）命令行：`-hvd` + hdc `127.0.0.1:5555`

- **现象**：不知如何脱离 IDE 起模拟器、装 HAP。
- **正确做法**：
  - 启动：`/Applications/DevEco-Studio.app/Contents/tools/emulator/Emulator -hvd "Pura 90"`（名见 `~/.Huawei/Emulator/deployed/*.ini`）。
  - 设备：`hdc list targets` → 常见 `127.0.0.1:5555`。
  - 安装：`hdc -t 127.0.0.1:5555 install entry/.../entry-default-unsigned.hap`。
  - 启动：`hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b <bundleName>`。
- **适用**：无 GUI / 脚本化调试。

## 13. 模拟器验不了局域网 TCP / mDNS / 设备发现

- **现象**：模拟器里 app 连不上局域网电视、ADB、mDNS 服务。
- **根因**：HVD 网络多为 NAT，**不是**与电脑同 Wi-Fi 的 peer；模拟器「代理设置」只影响 HTTP 出网，**不能**桥接局域网。
- **正确做法**：依赖局域网原始 TCP / mDNS 的链路（ADB 5555、插件 28100、无线调试配对）必须 **鸿蒙真机 + 与目标设备同 Wi-Fi**。模拟器只做 UI / 导航 / 无网逻辑。
- **适用**：任何局域网设备调试类 app。

## 14. ScanKit `generateBarcode` 在模拟器常失败

- **现象**：二维码区域一直 spinner / 空白，业务 payload（如配对码数字）已生成。
- **根因**：`@kit.ScanKit` 的 `generateBarcode.createBarcode` 在 HVD 或部分镜像不可用。
- **正确做法**：
  1. 调用时显式 `backgroundColor` / `pixelMapColor` / `margin`。
  2. `catch` 后 **纯逻辑矩阵兜底**（自研或库 → `image.createPixelMap` RGBA），保证有图。
  3. UI：仅生成中 spinner；失败出文案，禁止永久 loading（见 `dwy-arkts-ui-design.md`）。
- **适用**：任何依赖出码展示的页面。

## 文件职责（与本目录其它规则）

| 文件 | 管什么 |
|---|---|
| `dwy-arkts-strict.md` | 语言：禁用语法、arkts-no-* |
| `dwy-arkts-ui-build.md`（本文件） | 组件 API、状态、资源、构建、运行时/设备坑 |
| `dwy-arkts-ui-design.md` | **UI 设计规范**（弹层/顶栏/加载态/图标语义，事前约束） |
| `dwy-harmony-pitfalls.md` | 踩坑四栏归档（现象/根因/做法/适用），新坑先记这里再回写规范 |
