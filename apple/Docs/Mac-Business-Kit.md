# BusinessKitMac

`BusinessKitMac` 是 AppleAppKit 中可选的 macOS 业务 UI 产品。它把应用设置、购买、支持和账号页面组合进 `DesignKitMac` 的主题与控件。App 选择要使用的页面，并提供自己的内容、商品及服务。

在仓库根目录运行 `swift run MacBusinessGallery`，可预览共享界面和接入示例。示例账号和购买为本地模拟，文件保存、分享和偏好选择使用系统及基础库实现。示例源码位于 `apple/Examples/MacBusiness/Sources/MacBusinessGallery/`。

## 接入顺序

1. macOS target 链接 `BusinessKitMac`，使用一个 `BusinessPreferences` 实例。在主窗口、SwiftUI `Settings` 场景以及独立 AppKit 宿主根视图注入 `.businessPreferences(preferences, theme:)`。已有自定义配色可以传入应用的 `EControlTheme`。
2. 把 `BusinessSettingsPanel` 放入标准 `Settings` 窗口或原生 `.sheet`。每个 `BusinessSettingsSection` 提供稳定 ID、标题、SF Symbol 和任意 SwiftUI 内容。用 `BusinessGeneralSettings` 和 `BusinessAboutSettings` 组装通用分类。
3. 购买入口通过 `.macPaywall(isPresented:configuration:store:onUnlocked:)` 挂到所属窗口。用 `MacPaywallConfiguration` 配置标题、方案、权益和法律链接，从 StoreKit 商品取得实际价格。
4. 需要支持中心、快捷键、评分、账号或同步时，将下列组件装进自己的分类或独立视图。普通表单可以用 `MacBusinessSheet` 保持标题和底部操作可见。

| 能力 | 共享入口 | 应用提供 |
| --- | --- | --- |
| 语言、外观、字号 | `BusinessPreferences`、`BusinessGeneralSettings` | 支持语言、主题，或绑定既有偏好存储 |
| 购买、恢复与解锁 | `MacPaywallStore` 配 `LifetimeStore`、`StoreKitPurchaseStore` 或自有服务 | 商品 ID、推荐方案、权益要求和解锁后的操作 |
| 帮助与反馈 | `MacHelpCenter` | FAQ、文档链接、邮件或复制联系信息。作为 sheet 展示时传入 `onClose` |
| 文件保存、分享及日志 | `MacFileActions`、`MacFileActions.logs(fileNamePrefix:)` | 文件、生成数据，或日志文件名前缀。启用日志导出前初始化 App 自己的 LogKit 目录。已存在的文件由 App 持有访问权直到操作结束 |
| 快捷键 | `BusinessShortcutsView`、`BusinessShortcutStore` | 动作与默认组合。全局热键交给 App 提供的注册器，应用内动作使用得到的 `KeyboardShortcut` |
| 评分 | `BusinessReviewRow`、`BusinessReviewPrompter` | App Store 评分地址、触发事件、次数和冷却时间 |
| 登录与同步状态 | `BusinessAccountView`、`BusinessSyncView` | `AuthSessionStore`、登录入口以及 `SyncCoordinator` 或既有状态快照 |

## 应用自定义

`MacGlobalHotkey` 提供系统级热键注册。调用方传入 macOS 虚拟键码与 `NSEvent.ModifierFlags`，并在应用级状态持有返回的实例。注册失败会抛错，松键时在主线程调用动作。禁用或改绑前显式调用 `invalidate()`，确保旧组合立即释放。需要跟随连接、前后台或功能开关时，由宿主根据状态建立或释放注册。注册使用系统热键接口，无需监听所有按键或申请辅助功能权限。

`BusinessShortcutStore` 的全局设置仍通过 `applyGlobal` 接入。其设置按字符保存，`MacGlobalHotkey` 接收物理键码，宿主应采用与其录入方式一致的转换。只需要固定组合时可直接使用 `MacGlobalHotkey`。`MacBusinessGallery` 提供显式启停示例，并用热键调前主窗。

使用云端偏好的应用可以用 `BusinessGeneralSettings(languages:language:appearance:textSize:)` 接回自己的写入流程，并把生效的字号和语言注入各自窗口。登录、注销、同步开始和停止沿用应用的生命周期管理。

从 0.13.1 起，通用设置把语言、外观和字号放在同一张卡片中。菜单收起时按当前值布局，语言标签过长时截断，展开后显示完整选项。自有设置页可用 `EPicker(_:selection:selectedLabel:maxLabelWidth:content:)` 获得同样的宽度行为，并继续为菜单选项提供与绑定类型一致的 `tag`。

从已受限的操作打开购买时，在 `onUnlocked` 接收变更后的权益。业务操作等所属弹框关闭再继续，应用可根据返回的商品与自己的权益规则决定是否执行。

在消费 App 验收浅色、深色和增加对比度外观，检查菜单和快捷键、焦点恢复、权限弹框、文件访问与 StoreKit 沙盒购买。使用外部账号时另做登录与切号同步测试。
