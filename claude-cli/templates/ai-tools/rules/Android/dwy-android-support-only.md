---
description: Android 老项目强制使用 Support Library,禁止 AndroidX —— 依赖坐标、import、选库、gradle 配置全部遵循此规则
paths:
  - "**/*.java"
  - "**/*.kt"
  - "**/*.gradle"
  - "**/*.kts"
  - "**/gradle.properties"
---

# Android Support Library 专用规范(禁用 AndroidX)

## 适用前提(动手前先判断)

本规则**仅用于维护尚未迁移到 AndroidX 的 Support Library 老项目**。先判断当前项目属于哪一类:

- `gradle.properties` 有 `android.useAndroidx=true`,或代码中已大量 `import androidx.*` → 本项目**已是 AndroidX**,**本规则不适用**,按 androidx 正常开发,不要回退到 support
- 依赖 `com.android.support:*`、import `android.support.*`、无 `android.useAndroidx=true` → 本项目是 **Support 老项目**,严格遵循本规则

**理由**:Support 与 AndroidX 是同一套库前后两代的不同包名,**二者不可混用** —— 同一个类(如 `AppCompatActivity`)存在 `android.support.v7.app` 与 `androidx.appcompat.app` 两个包,混入后编译期报 `Duplicate class`、运行期 `NoClassDefFoundError`。老项目一旦混进 androidx,会陷入不可控的依赖地狱。要么整体维持 support,要么整体迁移 androidx,**禁止半迁移**。

## 一、依赖坐标

- 一律用 `com.android.support:*`,**禁止**任何 `androidx.*`
- Material 组件用 `com.android.support:design`,**禁止** `com.google.android.material:material`
- Support Library 版本**全项目统一锁定**(最后一个稳定版 `28.0.0`,可按项目实际调整,但所有 support 模块版本必须一致 —— 版本不一致会触发 `Manifest merger` / `Duplicate class` 报错)

```groovy
// ✅ Support
dependencies {
    implementation 'com.android.support:appcompat-v7:28.0.0'
    implementation 'com.android.support:recyclerview-v7:28.0.0'
    implementation 'com.android.support:design:28.0.0'
    implementation 'com.android.support:cardview-v7:28.0.0'
    implementation 'com.android.support.constraint:constraint-layout:1.1.3'
}

// ❌ AndroidX —— 一律禁止
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.0.4'
}
```

## 二、gradle.properties

```properties
# 禁用 AndroidX:必须为 false 或不声明(默认即 false)
android.useAndroidx=false
# 禁用 Jetifier:它会把第三方库的 support 依赖自动改写成 androidx,与本规则直接冲突
android.enableJetifier=false
```

## 三、import / 类引用

**禁止**任何 `import androidx.*` 与 `import com.google.android.material.*`。常用类映射(**用左列,禁右列**):

| 用途 | ✅ Support(用这个) | ❌ AndroidX(禁止) |
|---|---|---|
| AppCompatActivity | `android.support.v7.app.AppCompatActivity` | `androidx.appcompat.app.AppCompatActivity` |
| Fragment | `android.support.v4.app.Fragment` | `androidx.fragment.app.Fragment` |
| FragmentManager | `android.support.v4.app.FragmentManager` | `androidx.fragment.app.FragmentManager` |
| RecyclerView | `android.support.v7.widget.RecyclerView` | `androidx.recyclerview.widget.RecyclerView` |
| CardView | `android.support.v7.widget.CardView` | `androidx.cardview.widget.CardView` |
| Toolbar | `android.support.v7.widget.Toolbar` | `androidx.appcompat.widget.Toolbar` |
| ViewPager | `android.support.v4.view.ViewPager` | `androidx.viewpager.widget.ViewPager` |
| ConstraintLayout | `android.support.constraint.ConstraintLayout` | `androidx.constraintlayout.widget.ConstraintLayout` |
| ContextCompat | `android.support.v4.content.ContextCompat` | `androidx.core.content.ContextCompat` |
| ActivityCompat | `android.support.v4.app.ActivityCompat` | `androidx.core.app.ActivityCompat` |
| SwipeRefreshLayout | `android.support.v4.widget.SwipeRefreshLayout` | `androidx.swiperefreshlayout.widget.SwipeRefreshLayout` |
| DrawerLayout | `android.support.v4.widget.DrawerLayout` | `androidx.drawerlayout.widget.DrawerLayout` |
| LocalBroadcastManager | `android.support.v4.content.LocalBroadcastManager` | `androidx.localbroadcastmanager.content.LocalBroadcastManager` |
| Material 组件 | `android.support.design.widget.*`(TabLayout / NavigationView / FloatingActionButton / Snackbar 等) | `com.google.android.material.*` |

> 表中未列的类,按规律转换:`androidx.xxx` 的对应 support 包多在 `android.support.v4.*` / `android.support.v7.*` / `android.support.design.*` 下。拿不准时查 [AndroidX → Support 类映射](https://developer.android.com/jetpack/androidx/migrate/class-mappings) 反查。

## 四、选库规则(第三方依赖)

引入任何第三方库时,按顺序执行:

1. **优先选仍依赖 Support Library 的版本线**。库的较新版本若已迁移到 androidx,**锁定在最后一个支持 support 的版本**,并在依赖处注释说明原因与升级前置条件
2. 评估候选库先查其传递依赖:`./gradlew :app:dependencies`,确认无 `androidx.*` / `com.google.android.material` 渗入
3. 传递依赖混入 androidx 时,用 `exclude` 排除,并替换为 support 等价物;**无法排除或无 support 等价物 → 换库**,不要将就
4. **禁止**为使用某个只支持 androidx 的库而引入 androidx —— 一个 androidx 进来就破坏整套隔离,得不偿失

```groovy
// 库 foo 的 3.x 已迁 androidx,锁在最后支持 support 的 2.8.0(升级需先整体迁 androidx,见 issue #1234)
implementation 'com.foo:bar:2.8.0'

// 传递依赖混入 androidx,排除掉
implementation('com.legacy:sdk:1.5.0') {
    exclude group: 'androidx.appcompat'
    exclude group: 'androidx.core'
    exclude group: 'com.android.support'  // 同时排 support,防版本不一致,统一用项目锁定版
}
```

## 五、自检(选库 / 改依赖 / 写代码后强制执行)

**任一未通过 → STOP,立即修正。**

| # | 检查项 | 违规即 STOP |
|---|--------|------------|
| 1 | 无 `import androidx.*`、无 `import com.google.android.material.*` | ✓ |
| 2 | 依赖坐标全部 `com.android.support:*`,无 `androidx.*` / `com.google.android.material:material` | ✓ |
| 3 | 所有 support 模块版本一致(默认 `28.0.0`) | ✓ |
| 4 | `gradle.properties` 无 `android.useAndroidx=true`、无 `android.enableJetifier=true` | ✓ |
| 5 | 新引入第三方库经 `:dependencies` 核查无 androidx 传递依赖,有则 `exclude` 或换库 | ✓ |
| 6 | 为规避 androidx 而锁定版本的依赖,有注释说明原因与升级前置条件 | ✓ |

**不执行自检就提交代码 = 违规。**
