---
description: HarmonyOS ArkTS 严格性避坑（相对 TS/JS 的禁用语法，编译期 arkts-no-* 报错）
paths:
  - "**/*.ets"
  - "**/*.ts"
---

# ArkTS 严格性避坑

ArkTS 是 TypeScript 的**受限子集**，禁掉大量 TS/JS 动态写法以换取性能与静态可分析性。
从 TS/JS（尤其 iOS/前端转鸿蒙）照搬代码必触发 `arkts-no-*` 编译错误。
**写 `.ets` 前先过一遍本清单**，别用下面列出的禁用写法。每条配真实报错码 + 错误/正确写法。

## 1. 禁止解构声明与解构赋值（arkts-no-destruct-decls / arkts-no-destruct-assignment）

```typescript
// 错：解构声明
let [oldR, r] = [a % m, m];
// 错：解构赋值
[oldR, r] = [r, oldR - q * r];
const { value, next } = readVarint(bytes, i);

// 对：拆成单变量 + 临时变量交换
let oldR = a % m;
let r = m;
const tmpR = oldR - q * r;
oldR = r;
r = tmpR;
const res = readVarint(bytes, i);
const value = res.value;
const next = res.next;
```

## 2. 对象字面量必须对应显式 class/interface（arkts-no-untyped-obj-literals / arkts-no-obj-literals-as-types）

ArkTS 不允许「匿名对象字面量当类型」，也不允许「无类型标注的对象字面量」。
**两种触发场景都要先声明 interface**：

### 2.1 函数返回类型不能写匿名对象

```typescript
// 错：返回类型是匿名对象字面量
private static readVarint(bytes: Uint8Array, i: number): { value: number; next: number } { ... }

// 对：先声明 interface
interface VarintResult {
  value: number;
  next: number;
}
private static readVarint(bytes: Uint8Array, i: number): VarintResult { ... }
```

### 2.2 返回 / 赋值的对象字面量必须有类型来源

```typescript
// 错：裸对象字面量（编译器无法对应到具体类型）
return { command: c, arg0: a, arg1: b, dataLength: d };
const out = { header, payload: payload.slice() };

// 对：显式标注类型（interface 已声明）
const header: AdbHeader = { command: c, arg0: a, arg1: b, dataLength: d };
return header;
const out: AdbMessageResult = { header, payload: payload.slice() };
```

### 2.3 给 SDK API 传对象参数也要带类型

SDK（@ohos.net.socket / cryptoFramework 等）的参数即使是已声明类型，裸字面量仍报错，
必须用「声明类型的变量」传入：

```typescript
// 错：裸字面量传参
await tcp.connect({ address: { address: host, port: 5555, family: 1 }, timeout: 15000 });
await tcp.send({ data: buf });
const out = await signer.sign({ data: token });

// 对：拆成带 SDK 类型标注的变量
const netAddr: socket.NetAddress = { address: host, port: 5555, family: 1 };
const opts: socket.TCPConnectOptions = { address: netAddr, timeout: 15000 };
await tcp.connect(opts);

const sendOpts: socket.TCPSendOptions = { data: buf };
await tcp.send(sendOpts);

const input: cryptoFramework.DataBlob = { data: token };
const out = await signer.sign(input);
```

## 3. 禁止用下标访问 string 取字符（arkts-no-props-by-index）

string 不能 `s[i]` 取字符（被判为「字段索引访问」）。用 `charAt`：

```typescript
// 错
const table = 'ABCD...';
out += table[(n >> 18) & 63];

// 对
out += table.charAt((n >> 18) & 63);
```

> 注意：`Uint8Array[i]` / `Array[i]` 下标访问是允许的，只有 **string 下标取字符** 被禁。

## 4. 禁止 String() / Number() / Boolean() 当转换函数调用

ArkTS 禁止把内置构造器当函数转换值。catch 错误转文案、数字转字符串都要换写法：

```typescript
// 错
const msg = e instanceof Error ? e.message : String(e);
const s = String(num);

// 对：catch 变量在 ArkTS 里就是 Error（含 BusinessError extends Error），直接取 message
function errMsg(e: Error): string {
  return e.message;
}
// 数字转字符串用 .toString() 或模板串
const s = num.toString();
const s2 = `${num}`;
```

## 5. Promise executor / 回调形参类型：简单形参标，executor 的 resolve/reject 不标

箭头函数当回调，形参不能省类型；executor 里别把函数直接当回调透传：

```typescript
// 错：resolve 无类型 + 直接把 resolve 透传给 setTimeout
return new Promise<void>((resolve) => setTimeout(resolve, ms));

// 对：形参标类型 + 包一层箭头
return new Promise<void>((resolve: () => void) => {
  setTimeout(() => {
    resolve();
  }, ms);
});
```

**⚠️ 例外（实测踩坑）：给 `Promise` executor 的 resolve/reject 标注「函数类型」反而触发
`arkts-no-structural-typing`**。executor 的两个形参类型由 `Promise<T>` 自身约束，显式标
`(reject: (e: Error) => void)` 会与 SDK 内置的 reject 签名做结构比对而报错。这种情况**去掉
executor 形参的类型注解，让 ArkTS 推断**（reject 内部传 `Error` 子类实例完全正常）：

```typescript
// 错：executor 形参标函数类型 → arkts-no-structural-typing
return new Promise<Uint8Array>(
  (resolve: (v: Uint8Array) => void, reject: (e: Error) => void) => { ... });

// 对：executor 形参不标，推断
return new Promise<Uint8Array>((resolve, reject) => {
  reject(new MyError(...));   // MyError extends Error，正常
});
```

判据：**普通回调（如自己定义的 `onError: (e: Error) => void`）形参要标；`new Promise(...)`
的 executor 形参不标**。另：跨文件传回调时，形参类型用基类（`Error`）而非具体子类
（`MyGrpcError`），避免「子类型 lambda 赋给基类形参」触发同一规则。

## 6. 页面路由路径不带 `ets/` 前缀

`main_pages.json` 的 `src` 与 `windowStage.loadContent(...)` 的路径都相对 `src/main/ets/` 根，
**不要带 `ets/` 前缀**，否则编译报 `Page '.../ets/ets/xxx' does not exist`：

```json
// 错：resources/base/profile/main_pages.json
{ "src": ["ets/spike/SpikePage"] }
// 对
{ "src": ["spike/SpikePage"] }
```

```typescript
// 错
windowStage.loadContent('ets/spike/SpikePage', cb);
// 对
windowStage.loadContent('spike/SpikePage', cb);
```

## 7. 大整数运算用原生 bigint（无需第三方库）

ArkTS 原生支持 ES11 `bigint`（`10n` / `BigInt(x)` / `<< >> % & | ** /`）。
但无 `.inverse(m)` / `.power(_,modulus:)` / `.serialize()` 这类方法（那是 Swift BigInt 库的），
模逆/模幂/序列化要**手写**：

```typescript
// 模幂（快速幂）
function modPow(base: bigint, exp: bigint, m: bigint): bigint {
  let result = 1n;
  let b = base % m;
  let e = exp;
  while (e > 0n) {
    if ((e & 1n) === 1n) { result = (result * b) % m; }
    e >>= 1n;
    b = (b * b) % m;
  }
  return result;
}
// 模逆（扩展欧几里得，见本仓鸿蒙工程 AndroidPubkey.ets）
```

## 8. 自检清单（写完 .ets 提交前 grep 一遍）

```bash
grep -rn 'let \[\|const \[' .          # 解构声明
grep -rn '): {'  .                      # 匿名对象当返回类型
grep -rn 'return {' .                   # 裸对象字面量返回（确认有类型标注）
grep -rn 'String(\|Number(\|Boolean(' . # 构造器当转换函数（排除 String.fromCharCode）
grep -rn 'new Promise<.*>((.*:.*=>' .   # executor 形参标了函数类型（见 §5 例外，应去注解）
# string 下标取字符需人工核对（table[i] 形式）
```

## 9. 仍需真机/真实 SDK 确认的（编译期过不代表运行对）

ArkTS 编译通过只保证语法合规；以下 SDK 行为编译期无法验证，需真机/模拟器实测：
- cryptoFramework 的 `createSign(规格串)` 是否支持目标算法组合（如 `RSA2048|PKCS1|NoHash`）
- `getEncoded()` 返回的公钥 DER 是 PKCS#1 还是 X.509 SPKI（影响解析）
- `@ohos.net.socket.TCPSocket` 局域网连通性（需 `ohos.permission.INTERNET`，normal 级安装即授予）

---

> 本文件只管**语言语法层**。ArkUI 组件、V2 状态管理、图标资源、工程构建、运行时容错的坑
> 见同目录 **`dwy-arkts-ui-build.md`**（图标名映射 / 自定义组件链属性 / @BuilderParam 默认值 /
> @Param 外部初始化 / async 状态快照 / bootstrap 分步容错 / DevEco 命令行构建）。
