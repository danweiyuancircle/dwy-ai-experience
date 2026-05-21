---

## description: Android (Java + Kotlin + XML + Gradle) 代码注释与基础风格规范
paths:
  - "**/*.java"
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.gradle"
  - "**/AndroidManifest.xml"
  - "**/res/**/*.xml"

# Android 代码注释与基础风格规范

适用于 **Android 原生项目**(Java + Kotlin 混编,XML 布局,Gradle 构建脚本)。本规范**重点是代码注释**,兼带最小必要的命名 / 简约 / 反模式约束。

不限制构建工具、UI 框架、架构模式、SDK 版本、依赖库选型 —— 与老项目兼容。

## 一、命名规范


| 类型                                | 风格                                  | 示例                            |
| --------------------------------- | ----------------------------------- | ----------------------------- |
| 包                                 | `lowercase`                         | `com.example.user`            |
| 类 / 接口 / 枚举                       | `PascalCase`                        | `LoginActivity`、`UserAdapter` |
| 方法 / 函数                           | `camelCase`                         | `loadUserById()`              |
| 变量 / 参数                           | `camelCase`                         | `userCount`                   |
| 常量 (`static final` / `const val`) | `UPPER_SNAKE_CASE`                  | `MAX_RETRY_COUNT`             |
| Activity                          | `XxxActivity`                       | `LoginActivity`               |
| Fragment                          | `XxxFragment`                       | `HomeFragment`                |
| Adapter / ViewHolder              | `XxxAdapter` / `XxxViewHolder`      | `OrderAdapter`                |
| Dialog                            | `XxxDialog`                         | `ConfirmDialog`               |
| 布尔变量 / 方法                         | `is`* / `has*` / `can*` / `should*` | `isLoading`、`hasNext`         |


### 资源命名


| 资源类型            | 规则                       | 示例                                                                             |
| --------------- | ------------------------ | ------------------------------------------------------------------------------ |
| 布局文件            | `<类型>_<功能>.xml` 全小写下划线   | `activity_login.xml`、`fragment_home.xml`、`item_order.xml`、`dialog_confirm.xml` |
| View id         | `<控件类型>_<功能>`            | `tv_username`、`et_password`、`btn_submit`、`rv_orders`、`iv_avatar`               |
| drawable        | `<用途>_<状态>`              | `bg_button_primary`、`ic_arrow_right`、`shape_card_corner`                       |
| color           | `<语义>`                   | `color_primary`、`color_text_secondary`                                         |
| string          | `<场景>_<语义>`              | `login_button_submit`、`home_title`                                             |
| dimen           | `<语义>`                   | `padding_normal`、`text_size_title`                                             |
| anim / animator | `<逻辑名>_<方向|序号>` 或通用动画名   | `fade_in.xml`、`push_bottom_in.xml`、`loading_001.xml`                           |
| menu            | `menu_<场景>.xml`          | `menu_order_detail.xml`                                                        |
| style / theme   | `PascalCase`,点号继承,从通用到特殊 | `Widget.App.Button`、`Theme.App.Dark`                                           |
| mipmap          | 仅放启动图标 `ic_launcher*`    | `ic_launcher.webp`                                                             |
| raw / xml       | `<语义>` 全小写下划线            | `network_security_config.xml`、`bgm_login.mp3`                                  |


资源全部**小写 + 下划线**分词,**禁止**驼峰、大写、中划线(style / theme 除外,用 `PascalCase` + 点号继承)。

#### 控件 id 缩写对照表

View id 规则:`<控件缩写>_<逻辑名>`,如 `tv_username`、`btn_submit`。常用控件缩写:


| 类别      | 控件 = 缩写                                                                                                    |
| ------- | ---------------------------------------------------------------------------------------------------------- |
| 布局      | LinearLayout=`ll`、RelativeLayout=`rl`、ConstraintLayout=`cl`、FrameLayout=`fl`、TableLayout=`tl`              |
| 滚动 / 列表 | ScrollView=`sv`、NestedScrollView=`nsv`、ListView=`lv`、GridView=`gv`、RecyclerView=`rv`、ViewPager(2)=`vp`     |
| 文本 / 输入 | TextView=`tv`、EditText=`et`、Button=`btn`、ImageButton=`ib`                                                  |
| 展示      | ImageView=`iv`、WebView=`wv`、CardView=`cv`                                                                  |
| 选择 / 开关 | CheckBox=`cb`、RadioButton=`rbtn`、RadioGroup=`rg`、ToggleButton=`tb`、Switch=`sw`、Spinner=`spn`               |
| 进度      | ProgressBar=`pb`、SeekBar=`sb`、RatingBar=`rb`                                                               |
| 容器 / 导航 | Toolbar=`toolbar`、TabLayout=`tab`、FloatingActionButton=`fab`、BottomNavigationView=`bnv`、AppBarLayout=`abl` |


> 缩写冲突时取更长缩写消歧:`rbtn`(RadioButton) 区别于 `rb`(RatingBar)。表中无对应的控件,按"首字母 / 业务语义就近"自拟,组内保持一致。

#### drawable / selector 状态后缀

drawable 完整规则:`<模块_>业务功能_控件描述_状态`,如 `login_btn_pressed`、`tabs_icon_home_normal`。selector 多状态切换图统一用状态词后缀:


| 状态后缀         | 含义      |
| ------------ | ------- |
| `_normal`    | 默认 / 常态 |
| `_pressed`   | 按下      |
| `_focused`   | 聚焦      |
| `_selected`  | 选中      |
| `_checked`   | 勾选      |
| `_disabled`  | 禁用      |
| `_activated` | 激活      |


```text
res/drawable/
  selector_btn_login.xml       <!-- 状态选择器 -->
  bg_btn_login_normal.xml      <!-- 常态背景 -->
  bg_btn_login_pressed.xml     <!-- 按下背景 -->
  bg_btn_login_disabled.xml    <!-- 禁用背景 -->
```

#### mipmap / 9-patch / 模块前缀

- **mipmap 只放启动图标**(`ic_launcher` 系列),其余图片一律放 `drawable` —— mipmap 会跨密度保留资源,普通图放 mipmap 白白增大包体
- **9-patch 图保留 `.9` 后缀**:`bg_chat_bubble.9.png`
- **模块前缀(可选)**:多模块 / 大型项目推荐资源加业务模块前缀,便于检索、避免跨模块重名 —— `user_activity_login.xml`、id `user_tv_name`;单模块 / 老项目可省略,保持本规范其余示例的无前缀写法

### 禁止的写法

```kotlin
// ❌ 单字母变量(循环索引除外)
val d = getData()
// ✅
val userData = getData()

// ❌ 匈牙利命名
val strName = "Alice"
val lstUsers = mutableListOf<User>()
// ✅
val name = "Alice"
val users = mutableListOf<User>()

// ❌ 布尔变量不带语义前缀
val active = true
// ✅
val isActive = true
```

### 禁止魔法字符串与硬编码

- 同一字面量在文件内出现 **2 次及以上**必须提取为常量
- **所有用户可见文案必须走 `strings.xml`**,便于国际化与统一审校
- 颜色走 `colors.xml`,尺寸走 `dimens.xml`

```kotlin
// ❌ 散落
intent.putExtra("user_id", 123)
val id = intent.getLongExtra("user_id", 0)

// ✅ 常量化
class UserActivity : AppCompatActivity() {
    companion object {
        private const val EXTRA_USER_ID = "user_id"

        fun newIntent(context: Context, userId: Long) =
            Intent(context, UserActivity::class.java).putExtra(EXTRA_USER_ID, userId)
    }
}
```

```xml
<!-- ❌ 裸文案 / 裸数字 -->
<TextView android:text="登录" android:textSize="16sp" />

<!-- ✅ 走资源 -->
<TextView android:text="@string/login_button_submit" android:textSize="@dimen/text_size_normal" />
```

## 二、代码注释

### 总则

- 注释解释 **为什么(why)**,不复述 **做了什么(what)**
- 全部使用**中文**,**禁止**中英混用
- 类与方法注释**必须**有(不分可见性,一目了然的简单成员可省,见 §2.5 / §2.8),**禁止**简单的"获取 / 设置 / 处理"敷衍式注释
- 代码改动后**必须**同步更新注释,留下过时注释 = 违规

### 2.1 文件 / 类级注释(强制)

每个类(**不分可见性**,含 `private` / `internal` / 嵌套类 / 内部类)都必须有类级 Javadoc / KDoc,放在类声明上方,说明:

- 该类的**职责**
- 与谁配合工作(被谁调用、依赖谁)
- 关键的使用约束 / 生命周期 / 线程要求(如果有)

```kotlin
/**
 * 登录页。
 *
 * 负责账号密码 / 验证码登录入口,登录成功后跳转 [HomeActivity] 并清空回退栈。
 *
 * 入口:[newIntent] 静态构造,禁止外部直接 new Intent。
 */
class LoginActivity : AppCompatActivity() { ... }
```

```kotlin
/**
 * 订单列表 Adapter。
 *
 * 配合 [RecyclerView] + [DiffUtil] 增量刷新,UI 线程使用,**非线程安全**。
 *
 * @property onItemClick 列表项点击回调,参数为订单 ID
 */
class OrderAdapter(
    private val onItemClick: (orderId: Long) -> Unit,
) : ListAdapter<Order, OrderViewHolder>(DIFF_CALLBACK) { ... }
```

```java
/**
 * 用户头像加载工具。
 *
 * <p>封装默认占位图、圆角、错误图,所有头像加载必须走本类。
 */
public final class AvatarLoader {
    private AvatarLoader() {}
    ...
}
```

### 2.2 方法 / 函数注释(强制)

所有方法 / 函数(**不分可见性**,含 `private` / `internal` / 顶层函数)必须有 Javadoc / KDoc,包含:

- 一句话功能描述
- `@param` 每个参数的语义、取值范围、可空性
- `@return` 返回值语义,空集合 / null 含义
- `@throws` 可能抛出的异常 + 触发条件
- 涉及线程 / 主线程要求时**必须**注明

例外:一目了然的简单 getter / setter、测试方法可省(详见 §2.5 / §2.8)。私有方法注释重点写**为什么这样实现**,不复述代码。

```kotlin
/**
 * 根据 ID 查询用户。
 *
 * 内部走内存缓存 → DB → 网络的三级回源,网络超时 5 秒。
 * 必须在后台线程调用,**禁止主线程**。
 *
 * @param userId 用户唯一标识,必须 > 0
 * @return 匹配的用户对象;不存在时抛 [NotFoundException],不返回 null
 * @throws NotFoundException 用户不存在
 * @throws IOException 网络请求失败且本地无缓存
 */
fun getUserById(userId: Long): User { ... }
```

```java
/**
 * 启动登录页。
 *
 * <p>调用方所在 Activity / Fragment 不需要预先清栈,本方法内部已带 {@code FLAG_ACTIVITY_CLEAR_TOP}。
 *
 * @param context 启动上下文,Activity / Application 均可
 * @param redirectUri 登录成功后跳转的目标 URI,可为 null;为 null 时跳首页
 */
public static void start(@NonNull Context context, @Nullable String redirectUri) { ... }
```

### 2.3 Activity / Fragment 注释模板(强制)

页面类**必须**在类级注释中注明:**入口方式、关键参数、返回结果(如有)**。

```kotlin
/**
 * 订单详情页。
 *
 * 入口:[newIntent],必须传入 [EXTRA_ORDER_ID]。
 * 返回:取消订单成功时 setResult [RESULT_ORDER_CANCELED],携带 [EXTRA_ORDER_ID]。
 */
class OrderDetailActivity : AppCompatActivity() {

    companion object {
        private const val EXTRA_ORDER_ID = "order_id"
        const val RESULT_ORDER_CANCELED = 1001

        /**
         * 构造启动订单详情页的 Intent。
         *
         * @param context 启动上下文
         * @param orderId 订单 ID,必须 > 0
         */
        fun newIntent(context: Context, orderId: Long): Intent =
            Intent(context, OrderDetailActivity::class.java)
                .putExtra(EXTRA_ORDER_ID, orderId)
    }
}
```

### 2.4 回调 / 监听器注释(强制)

回调参数必须注明每个参数的语义,以及回调发生的**线程**。

```kotlin
/**
 * 文件下载回调。所有方法在**主线程**触发。
 */
interface DownloadListener {
    /**
     * 下载进度更新。
     *
     * @param downloaded 已下载字节数
     * @param total 文件总字节数;-1 表示未知大小
     */
    fun onProgress(downloaded: Long, total: Long)

    /** 下载完成,[file] 为最终落盘路径。 */
    fun onSuccess(file: File)

    /** 下载失败,[error] 为失败原因,UI 层负责展示提示。 */
    fun onError(error: Throwable)
}
```

### 2.5 复杂方法 / 业务规则注释(强制)

涉及**业务规则、边界条件、为什么这样写**时必须有注释。简单 getter / setter / 一目了然的方法可省。

```kotlin
// ❌ 无用注释,只复述代码
// 获取用户
val user = userRepo.getById(userId)

// ✅ 解释原因
// 此处必须用本地缓存,因为退到后台超过 30 分钟会被系统回收,
// 网络回源会触发整页重绘,体验差
val user = userCache.getById(userId)
```

```kotlin
fun computeDiscount(order: Order): BigDecimal {
    // 业务规则(2024-12 起):VIP 用户首单 8 折,后续 9 折,叠加优惠券时取较低者
    // 详见需求 PRD-2401-折扣调整
    if (order.isFirstOrder && order.user.isVip) {
        return order.amount.multiply(BigDecimal("0.8"))
    }
    ...
}
```

### 2.6 字段 / 属性注释(强制)

公开字段、`data class` 字段、配置常量必须逐个注释。

```kotlin
/**
 * 用户信息。
 *
 * @property id 用户 ID,服务端分配,> 0
 * @property name 昵称,1-32 字符
 * @property avatarUrl 头像地址,空字符串表示无头像(不为 null)
 * @property vipLevel 会员等级,0=普通,1=VIP,2=SVIP
 */
data class User(
    val id: Long,
    val name: String,
    val avatarUrl: String,
    val vipLevel: Int,
)
```

```java
public final class Constants {
    /** 登录态本地缓存的 SP key,迁移版本时不允许复用此 key,会读到旧数据。 */
    public static final String SP_KEY_LOGIN_TOKEN = "login_token_v2";

    /** 网络请求超时,单位毫秒。短于 3000 易在弱网误判,长于 15000 用户感知卡顿。 */
    public static final int NETWORK_TIMEOUT_MS = 8000;
}
```

### 2.7 XML 资源注释(强制)

`strings.xml` / `colors.xml` / `dimens.xml` 中超过一屏的资源**必须**分组,每组用 `<!-- -->` 注释说明用途。

```xml
<!-- res/values/strings.xml -->
<resources>
    <!-- 通用 -->
    <string name="app_name">我的应用</string>
    <string name="confirm">确定</string>
    <string name="cancel">取消</string>

    <!-- 登录 / 注册 -->
    <string name="login_title">登录</string>
    <string name="login_hint_username">请输入手机号</string>
    <string name="login_hint_password">请输入密码</string>
    <string name="login_button_submit">登录</string>

    <!-- 错误提示 -->
    <string name="error_network_unavailable">网络不可用,请检查后重试</string>
    <string name="error_server_busy">服务器繁忙,请稍后再试</string>
</resources>
```

布局文件中重要节点(如自定义复杂组件)用 `<!-- -->` 标注职责:

```xml
<!-- 顶部状态条:展示订单状态色块 + 状态文案,根据 OrderStatus 切换 -->
<LinearLayout
    android:id="@+id/ll_status_bar"
    ... />
```

### 2.8 注释规范汇总


| 场景                        | 风格                                                 | 必填  |
| ------------------------- | -------------------------------------------------- | --- |
| 单行可描述清楚                   | 单行 KDoc/Javadoc:`/** xxx。 */`                      | ✓   |
| 有参数 / 返回值 / 异常            | 多行,含 `@param` / `@return` / `@throws`              | ✓   |
| Activity / Fragment       | 必须注明入口、参数 key、返回结果                                 | ✓   |
| 回调接口                      | 必须注明触发线程 + 每个参数语义                                  | ✓   |
| `data class` 字段           | Kotlin `@property`,Java 字段上 `/** */`               | ✓   |
| 复杂业务规则                    | 行内注释解释 why + 关联 PRD / 需求号                          | ✓   |
| 重写方法                      | `@inheritDoc` 或重新写明覆写差异                            | ✓   |
| Gradle 脚本(Groovy)         | 解释 why:锁版本/exclude 原因、变体用途、自定义 task/方法语义(详见 §2.10) | ✓   |
| 简单 getter / setter / 一目了然 | 可省                                                 | —   |
| 测试方法                      | 测试名本身就是描述,可省                                       | —   |


### 2.9 行内注释禁止事项

```kotlin
// ❌ 复述代码
// i 自增
i++

// ❌ 注释掉的代码块(用 git 历史,不要留垃圾)
// val old = legacyService.fetch()
// ...
val data = newService.fetch()

// ❌ TODO 不带责任人 / 时间 / 关联 issue
// TODO: 这里有点问题

// ✅ TODO 必须带责任人 + 日期 + 上下文
// TODO(zhang, 2026-05-30): 兼容企业微信扫码,关联 issue #1234
```

### 2.10 Gradle 脚本注释(Groovy)

老项目的 `build.gradle` / `settings.gradle` 多用 **Groovy** 编写(新项目 Kotlin DSL `*.gradle.kts` 同理)。构建脚本是声明式配置,注释**只解释"为什么这样配",不复述配置项字面**。

注释语法:`//` 单行、`/* */` 多行、`/** */` Groovydoc(自定义方法用),全部**中文**。

**必须注释的场景**:

- 依赖锁死/降级版本、`exclude` / `force` / `resolutionStrategy` —— 写明原因(冲突、漏洞、兼容)
- 非常规依赖(为绕过某 bug、临时分支版本)—— 写明来源与可移除条件
- `buildTypes` / `productFlavors` / `signingConfigs` —— 每个变体的用途、签名/密钥来源
- 自定义 `task`、`ext` 变量、`def` 方法 —— 用途、单位、输入输出
- 关键魔法值(`minSdk` / `targetSdk` 选定依据、超时、内存参数)

```groovy
android {
    defaultConfig {
        // minSdk 23:线上 92% 设备覆盖,低于 23 的指纹 API 需大量兼容代码,收益不抵成本
        minSdk 23
        targetSdk 34
    }

    buildTypes {
        release {
            // 走 CI 注入的正式签名,密钥在 Jenkins 凭据(credentialsId: android-release-key),禁止入库
            signingConfig signingConfigs.release
            minifyEnabled true
        }
    }
}

dependencies {
    // 锁 4.9.3:4.10+ 要求 minSdk 24,与本项目 minSdk 23 冲突,升级需先抬 minSdk
    implementation 'com.squareup.okhttp3:okhttp:4.9.3'

    // 排除传递依赖的旧 support 库,避免与 androidx 冲突(报 Duplicate class)
    implementation('com.legacy:sdk:2.1.0') {
        exclude group: 'com.android.support'
    }
}

/**
 * 读取 local.properties 中的密钥,缺失时回退空串(本地开发无需打正式包)。
 *
 * @param key 属性名
 * @return 属性值;不存在时返回空字符串
 */
def localProp(String key) {
    def f = rootProject.file('local.properties')
    return f.exists() ? new Properties().with { load(f.newReader()); getProperty(key, '') } : ''
}
```

**禁止**(同 §2.9):复述配置字面(`// 设置 minSdk`)、注释掉的依赖/配置块、不带责任人的 TODO。

## 三、可空性

### Kotlin

- 默认所有类型不可空,可空显式 `?`
- **禁止** `!!` 出现在生产代码,除非附注释说明为什么一定不为 null

```kotlin
// ❌ !! 滥用
val name = user!!.profile!!.nickname!!

// ✅ 安全调用 + 兜底
val name = user?.profile?.nickname ?: getString(R.string.user_anonymous)
```

### Java

- 公开 API 参数 / 字段 / 返回值用 `@Nullable` / `@NonNull`(`androidx.annotation.*`) 标注
- 集合返回值优先返回空集合而非 `null`

```java
// ❌ 没有可空标注
public User findById(long id) { ... }

// ✅
@Nullable
public User findById(long id) { ... }

@NonNull
public List<Order> findOrders(long userId) {
    return repository.queryByUser(userId);
}
```

### 禁止 `Object` / `Any` 当懒标注

- Java **禁止**用 `Object` 当 API 入参 / 返回值(反射框架边界除外)
- Kotlin **禁止**用 `Any` / `Any?`(JSON tree、反射桥接除外)
- 必须使用时**附注释说明原因**

## 四、函数 / 类设计与包组织

### 强制规则

- 公开方法 / 函数参数 ≤ **3 个**,超过则封装为 DTO / `data class`
- Kotlin 优先**命名参数 + 默认参数**代替方法重载
- 函数体不超过 **50 行**,超过则拆分
- 单文件不超过 **500 行**,超过则拆分模块
- 嵌套不超过 **3 层**,使用 early return / `?.let` / `return@xxx` 降低嵌套
- 类字段 / Kotlin 主构造参数 ≤ **7 个**,超过则按职责拆分

```kotlin
// ❌ 多个布尔参数 + 重载
fun share(toWechat: Boolean, toQQ: Boolean, withImage: Boolean)

// ✅ 命名参数 + 枚举
enum class ShareChannel { WECHAT, QQ, WEIBO }
fun share(channel: ShareChannel, withImage: Boolean = false)
```

```kotlin
// ❌ 深层嵌套
fun process(user: User?) {
    if (user != null) {
        if (user.isActive) {
            if (user.orders.isNotEmpty()) {
                user.orders.forEach { ... }
            }
        }
    }
}

// ✅ 提前返回
fun process(user: User?) {
    if (user == null || !user.isActive) {
        return
    }
    if (user.orders.isEmpty()) {
        return
    }
    user.orders.forEach { ... }
}
```

### 控制流大括号

`if` / `else` / `else if` / `for` / `while` / `do-while` **即使只有一条语句**,必须使用 `{}` 包裹。

**理由**:

- 后续添加第二行时不会因为漏 `{}` 静默脱出条件体(经典回归 bug)
- IDE 自动 reformat 与跨工具 merge 不会错位
- Java 与 Kotlin 视觉一致,混编项目无歧义

**例外**:Kotlin **表达式形式**的 `if`(用作赋值右值、`return` 表达式、单表达式函数体)允许单行无 `{}`:

```kotlin
val name = if (user.isVip) user.vipName else user.nickname    // ✅ 表达式 if
return if (cond) doA() else doB()                              // ✅ 表达式 if
fun grade(score: Int) = if (score >= 60) "PASS" else "FAIL"    // ✅ 单表达式函数
```

**反例**:

```kotlin
// ❌ 单行 if 语句无大括号 — 后续加一行就出 bug
if (!initialized.compareAndSet(false, true)) return

// ❌ 单行 for / while
for (item in list) item.refresh()
while (queue.isNotEmpty()) queue.poll().run()
```

```java
// ❌ Java 同样禁止
if (user == null) return;
for (Order o : orders) o.cancel();
```

**正例**:

```kotlin
// ✅ if 语句必须 {}
if (!initialized.compareAndSet(false, true)) {
    return
}

for (item in list) {
    item.refresh()
}

while (queue.isNotEmpty()) {
    queue.poll().run()
}
```

```java
// ✅ Java 同样
if (user == null) {
    return;
}

for (Order o : orders) {
    o.cancel();
}
```

### 包组织(按功能聚合)

**按功能聚合(package-by-feature),不按技术分层(package-by-layer)。**

同一个功能/页面相关的所有类 —— 页面(Activity / Fragment)、其数据实体、业务逻辑(ViewModel / Presenter / UseCase)、数据访问(Repository)、列表 Adapter、UI 状态等 —— 放在**同一个功能包**下聚合,而不是按类型横切成 `activities/`、`models/`、`adapters/`、`repositories/` 这种分层包。

**理由**:改一个功能时,相关文件都在一个包内,无需在多个分层目录间跳转;包之间按业务边界解耦,删除/迁移一个功能只动一个包;高内聚低耦合,符合就近维护。

```text
// ✅ 按功能聚合
com.example.app/
  login/                      <!-- 登录功能,自包含 -->
    LoginActivity.kt
    LoginViewModel.kt
    LoginRepository.kt
    LoginUiState.kt
    Credential.kt             <!-- 该功能私有实体 -->
  order/                      <!-- 订单功能 -->
    OrderListActivity.kt
    OrderDetailActivity.kt
    OrderViewModel.kt
    OrderRepository.kt
    OrderAdapter.kt
    Order.kt
  common/                     <!-- 跨功能共享:基类、工具、网络、通用实体 -->
    base/  network/  util/  model/

// ❌ 按技术分层横切 —— 改一个功能要在多个目录间反复跳
com.example.app/
  activities/   LoginActivity.kt  OrderListActivity.kt  OrderDetailActivity.kt
  viewmodels/   LoginViewModel.kt  OrderViewModel.kt
  repositories/ LoginRepository.kt  OrderRepository.kt
  adapters/     OrderAdapter.kt
  models/       Credential.kt  Order.kt
```

**约束**:

- 功能包名用业务语义小写单词(`login` / `order` / `profile`),不用 `ui` / `data` 等分层词作为顶层
- 仅某功能使用的实体/工具,放该功能包内,可设 `internal` 收敛可见性;**被 2 个及以上功能共享**才上提到 `common/`
- 功能包内可再按需细分子包(如复杂功能 `order/detail/`、`order/list/`),但仍以功能而非类型划分

## 五、Context 与内存泄漏

- **禁止**长生命周期对象(单例、静态字段、长任务)持有 Activity / Fragment / View 引用
- 单例需要 Context 时**必须** `applicationContext`
- Handler 内部类必须 `static` + `WeakReference`(Java)
- Bitmap / Cursor / InputStream 必须 `use { ... }`(Kotlin) / try-with-resources(Java) 释放
- Fragment 中持有的 View 引用在 `onDestroyView` 必须置 null
- 监听器 / 广播注册成对(`onStart/onStop` 或 `onResume/onPause`),**禁止**在 `onCreate` 注册、`onDestroy` 解注册(横屏切换重建会泄漏)

```kotlin
// ❌ 持有 Activity Context
object UserManager {
    var context: Context? = null  // Activity 销毁后泄漏
}

// ✅ ApplicationContext
object UserManager {
    private lateinit var appContext: Context
    fun init(context: Context) { appContext = context.applicationContext }
}
```

## 六、错误处理

### 强制规则

- UI 层**必须** try/catch 捕获预期异常并展示用户友好提示;**禁止**让异常崩溃到 `Thread.UncaughtExceptionHandler`
- **禁止** `catch (Exception e) {}` 空捕获
- **禁止** `catch (Throwable t)`(会吞 OOM / StackOverflow)
- **禁止** `e.printStackTrace()`,改用项目自有日志工具

## 七、代码简约原则

### 核心思想

代码只写**必要的逻辑**,不写"以防万一"的冗余。信任内部代码与框架保证,只在系统边界(用户输入、网络响应、IPC)做校验。

```kotlin
// ❌ 不必要的 fallback — user.name 类型已是非空 String
val name = user.name ?: ""

// ✅
val name = user.name

// ❌ 不必要的异常兜底 — 掩盖 bug
val result = try {
    calculate(x)
} catch (e: Exception) {
    0
}

// ✅ 让异常暴露,或只捕预期类型
val result = calculate(x)
```

### 判断标准

写每一行防御代码前问自己:**这个情况在当前上下文下真的会发生吗?**

- **会** → 写防御,加注释说明触发条件
- **不会** → 不写,信任上游保证
- **不确定** → 查看调用链确认,不要"以防万一"

## 八、常见反模式(禁止)


| 反模式                                                               | 正确做法                                        |
| ----------------------------------------------------------------- | ------------------------------------------- |
| Kotlin `!!` 非空断言                                                  | `?:` / `requireNotNull(x) { "..." }` 并附错误信息 |
| `catch (Exception e) {}` 空块                                       | 只捕获预期具体异常,或重新抛                              |
| `catch (Throwable t)`                                             | 只捕预期类型,OOM / StackOverflow 不该兜              |
| `e.printStackTrace()`                                             | 项目自有日志工具                                    |
| Java `==` 比较对象                                                    | `Objects.equals(a, b)` / `a.equals(b)`      |
| Kotlin `===` 滥用                                                   | 仅在确实需要引用相等时使用                               |
| 暴露内部可变集合                                                          | 返回不可变副本                                     |
| 静态可变状态 / 单例存 UI 数据                                                | 局部状态 / 持久化存储                                |
| Kotlin 顶层 `var`                                                   | `val`;需可变用类封装 + 同步原语                        |
| 内部类持有外部 Activity                                                  | `static` 内部类 + `WeakReference`              |
| 拼接 SQL 字符串                                                        | 参数化查询                                       |
| 硬编码 dp / sp 值                                                     | `@dimen/`                                   |
| 硬编码颜色值 `#FF0000`                                                  | `@color/color_primary`                      |
| 用户可见文案硬编码                                                         | `@string/...`                               |
| 单行 `if` / `for` / `while` / `do-while` 无 `{}`(Kotlin 表达式 `if` 除外) | 即使只一行也写 `{}`;详见 §四「控制流大括号」                  |


## 九、代码自检(写代码时强制执行)

**每次生成或修改 Android 代码后,必须逐条验证。任一未通过 → STOP,立即修正。**


| #   | 检查项                                                                                                                                                                                                                       | 违规即 STOP |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1   | 每个类(含 `private` / `internal` / 嵌套类)有类级 Javadoc / KDoc(中文),说明职责与协作关系                                                                                                                                                       | ✓        |
| 2   | 方法 / 函数(不分可见性)有 Javadoc / KDoc,含 `@param` / `@return` / `@throws`;一目了然的简单 getter / setter、测试方法可省                                                                                                                          | ✓        |
| 3   | Activity / Fragment 类注释包含入口、参数 key、返回结果                                                                                                                                                                                   | ✓        |
| 4   | 回调接口注明每个参数语义 + 触发线程                                                                                                                                                                                                       | ✓        |
| 5   | `data class` / 公开字段 / 配置常量逐个 `@property` / 字段注释                                                                                                                                                                           | ✓        |
| 6   | 复杂业务逻辑有"why"行内注释,关联 PRD / 需求号                                                                                                                                                                                             | ✓        |
| 7   | 注释全部中文,无中英混用,无敷衍式"获取 / 设置 / 处理"                                                                                                                                                                                           | ✓        |
| 8   | 注释与代码同步更新,无过时注释                                                                                                                                                                                                           | ✓        |
| 9   | 公开方法参数 + 返回值类型完整,无 `Object` / `Any` 懒标注                                                                                                                                                                                   | ✓        |
| 10  | Kotlin 无 `!!`(必须使用时附注释说明)                                                                                                                                                                                                 | ✓        |
| 11  | Java 公开 API 用 `@Nullable` / `@NonNull` 标注                                                                                                                                                                                 | ✓        |
| 12  | 单例 / 长生命周期对象用 `applicationContext`,不持有 Activity                                                                                                                                                                           | ✓        |
| 13  | 用户可见文案走 `strings.xml`,颜色走 `colors.xml`,尺寸走 `dimens.xml`                                                                                                                                                                   | ✓        |
| 14  | 同一文件内字符串字面量 ≥ 2 次必须提取为常量                                                                                                                                                                                                  | ✓        |
| 15  | 无空 `catch` 块、无 `catch (Throwable)`、无 `e.printStackTrace()`                                                                                                                                                                | ✓        |
| 16  | 嵌套不超过 3 层,函数体不超过 50 行,单文件不超过 500 行                                                                                                                                                                                        | ✓        |
| 17  | 资源命名遵守:layout 前缀(`activity_`* / `fragment_*` / `item_*`)、id 控件缩写(`tv_*` / `et_*` / `btn_*` / `rv_*` …)、drawable / selector 状态后缀(`_normal` / `_pressed` / `_disabled` …)、anim / menu / style / mipmap 命名,9-patch 带 `.9` 后缀 | ✓        |
| 18  | 无注释掉的代码块(垃圾代码),TODO 必须带责任人 + 日期 + 上下文                                                                                                                                                                                     | ✓        |
| 19  | `if` / `else` / `else if` / `for` / `while` / `do-while` 语句即使单行也带 `{}`(Kotlin 表达式 `if` 除外)                                                                                                                                | ✓        |
| 20  | 新增类按**功能聚合**放对应功能包(`login/` / `order/`),不按 `activities/` / `models/` 分层横切;仅多功能共享才放 `common/`                                                                                                                              | ✓        |
| 21  | Gradle 脚本(Groovy / kts):锁版本 / `exclude` / 自定义 task / 变体 / 关键魔法值有 why 注释,无复述式、无注释掉的配置块                                                                                                                                     | ✓        |


**不执行自检就提交代码 = 违规。**