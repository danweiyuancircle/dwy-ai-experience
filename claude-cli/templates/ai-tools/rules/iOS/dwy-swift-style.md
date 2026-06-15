---
paths:
  - "**/*.swift"
---

# Swift 代码规范

编辑任何 `.swift` 时遵守。本规则仅覆盖代码写法层（缩进、命名、注释、控制流、UI token 化），是与具体业务无关的通用约定。

## 1. 缩进与格式

- **4 空格缩进**，不用 Tab。
- 类型 / 函数声明参数过长时换行，每参数一行，右括号与返回类型 `) -> X` 单起一行。
- 一行只做一件事，避免把多个 `if` 挤进一行。

## 2. 命名

- 类型 `UpperCamelCase`，属性 / 方法 / 局部变量 `lowerCamelCase`。
- **局部短生命周期变量可用短名**（`i` = index、`f` = formatter、`cal` = calendar），同一文件内保持一致。
- 名字表达意图，避免无信息量的 `data` / `info` / `tmp` 当主力变量名。

## 3. 类型声明（iOS 17）

状态对象统一 iOS 17 写法，不要 `ObservableObject / @Published / @StateObject`：

```swift
@MainActor                  // 所有触碰 UI / 主线程隔离状态的类型都标
@Observable                 // 替代 ObservableObject
final class ListViewModel { // 非继承类一律 final
    private let store: DataStore  // 依赖私有 + 构造注入
}
```

## 4. 注释（中文，强制全量）

**所有代码都要加注释，包括每个类型和每个方法**。注释说明**意图**（为什么这么做、约束是什么），而非复述代码字面。

- **类型顶部必加** `///` 文档注释：说明该类型的职责、它在数据流里的位置或关键约束。`class` / `struct` / `enum` / `protocol` / 有逻辑的 `extension` 都算。
- **每个方法 / 函数必加** `///` 文档注释（公开和私有都要），说明它做什么、入参出参的语义、可能抛出的错误。
- 关键属性、反直觉分支、易踩坑处用行内 `//` 标注触发条件。
- 注释里**禁止 emoji**。
- 不写废话注释（`// 设置 name` 这种复述赋值的删掉），注释要补充代码没说出口的信息。

```swift
/// 列表数据源。负责从持久层读取并按时间分组，供视图直接渲染。
@MainActor
@Observable
final class ListViewModel {

    /// 重新加载全部数据并写回 `grouped`。
    /// 失败时透传持久层错误，由调用方决定提示策略。
    func reload() throws {
        let items = try store.all()        // 持久层已保证非 nil，无需兜底
        grouped = group(items)
    }
}
```

## 5. 控制流：信任上游，不过度防御

只在系统外边界（用户输入、文件 / 网络读入、外部 API）校验；内部调用信任类型签名。

```swift
// 好：early return，无多余 else
guard !isBusy else { return }
withAnimation(.spring(response: 0.5, dampingFraction: 0.75)) { isBusy = true }
```

- 不写 `value ?? default` 兜已有明确来源的值。
- 不写 `try? { ... }` 吞异常掩盖 bug；只 catch 预期的具体错误，其余让它抛。
- 持久 / IO 层方法用 `throws` 透传错误，由调用方决定处理，不在底层吞。

## 6. 图标：矢量图，禁止 emoji

UI 图标优先使用 **SF Symbols 矢量图**（`Image(systemName:)`）。系统无对应符号时，改用**成熟第三方 SVG 图标**（如已集成并维护良好的 icon 套件），禁止自行手绘或临时 PNG/emoji。

```swift
// 优先：系统 SF Symbols
Image(systemName: "checkmark")
    .font(.system(size: 11, weight: .bold))
    .foregroundStyle(.white)

// 次选：成熟第三方矢量图标组件或资源
Image("icon_checkmark")
    .resizable()
    .frame(width: 12, height: 12)

// 禁止：emoji 当图标
Text("✅")   // 不允许
```

任何视图、文案、注释都**禁止 emoji**。

## 7. 颜色 / 字体 / 动效 token 化

- 颜色集中到设计 token（如 `ColorTokens.*` / `theme.*`），**禁止在视图里散落硬编码颜色字面量**。
- 字体用 `.font(.system(size:weight:))` 或集中的字体 token。
- 动效统一用一组 `.spring(response:dampingFraction:)` 参数，不用 `.easeInOut`，保持全局手感一致。

## 8. 文案与时间

- 所有 UI 文案走 `String(localized: "some_key")`，**禁止硬编码字面量**；key 命名风格全项目统一。
- 业务逻辑里「现在」作为依赖注入（`now: @escaping () -> Date = { Date() }`），方便单测固定时间，禁止在逻辑里直接散用 `Date()`。
