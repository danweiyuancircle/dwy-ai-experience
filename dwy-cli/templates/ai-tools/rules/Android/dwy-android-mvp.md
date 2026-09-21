---
description: Android 手写 Contract MVP；业务 BaseActivity / BaseFragment / BaseDialog 落在 BizFoundation；简单静态页和确认框允许无 Presenter
paths:
  - "**/*.java"
  - "**/*.kt"
  - "**/AndroidManifest.xml"
  - "**/res/**/*.xml"
---

# Android MVP 与业务 Base

页面内部分工。模块四层见 `dwy-android-layering`；注释 / 命名 / AppCompat 见 `dwy-android-core`。

手写 Contract MVP，**禁止**引入 Mosby / Moxy / Nucleus。Support 与 AndroidX 跟当前项目推断，本文件不写死 import。

新页面强制本结构。存量不回溯改老 Activity；新加的页必须走本文件。

---

## 一、和四层怎么接

```
框架 AppCompatActivity / Fragment / DialogFragment
        ↑
:biz-foundation
  BaseActivity / BaseFragment / BaseDialog     ← 本产品壳
        ↑
:features:orders
  OrderListActivity extends BaseActivity
  implements OrderListContract.View
```

| 类 | 层 | 装什么 | 不装什么 |
|---|---|---|---|
| （无页面基类） | Foundation | Http / Log / 工具 | 标题栏、登录态、业务 loading、Activity 基类 |
| `BaseActivity` `BaseFragment` `BaseDialog` | **BizFoundation** | 本产品跨 Feature 的壳：标题、loading、toast、登录失效、inset、AutoSize `getResources` | 某个 Feature 的列表 / 下单 / 表单 |
| `XxxActivity` + `XxxContract` + `XxxPresenter` | Features | 该页 UI 与业务 | 再写一套 Base |

未拆四层的存量仓：Base* 可放 `common/base`，职责仍是本产品壳，不是某个 Feature。

---

## 二、业务 Base（强制）

产品自己的 Base，用来给业务扩展，不是框架自带的 `AppCompatActivity`。

- Feature 页面 **禁止** 直接继承 `AppCompatActivity` / 原生 `Fragment` / 裸 `Dialog`（有业务 Base 之后）
- Foundation **禁止** 出现带本产品语义的页面基类（换产品带不走）
- Base* **禁止** 上帝类：不准出现 `initOrder()`、`loadUser()`、某 Feature 控件 id
- `BaseDialog` 新代码默认 **DialogFragment**（有生命周期，Presenter 才好 detach）。存量已是 `Dialog` 子类的不强制迁

BizFoundation 可提供一对很薄的口，给所有页复用，不是业务：

- `IBaseView`：`showLoading` / `hideLoading` / `showError` / `showToast`
- `BasePresenter<V>`：`attach` / `detach` / `isAttached()`
- `BaseActivity` / `BaseFragment` / `BaseDialog` 实现 `IBaseView`

---

## 三、Contract MVP

有请求、状态、校验、跨控件协作的屏幕，一套三类，**按功能聚合在同一包**（禁止全局 `presenters/` / `contracts/`）：

```
features/orders/list/
  OrderListContract.java      // View + Presenter 接口
  OrderListActivity.java      // extends BaseActivity implements View
  OrderListPresenter.java     // 实现 Presenter
  OrderListRepository.java    // 数据；不强制再套 XxxModel
```

| 角色 | 做什么 | 禁止 |
|---|---|---|
| **Contract.View** | UI 意图：`showList` / `showEmpty` / `showError` | 接口里出现 `TextView` / `RecyclerView` / Activity |
| **Presenter** | 业务与请求编排 | 持有 Activity / Context / 控件；`findViewById` |
| **页面** | 实现 View、绑控件、把用户动作转给 Presenter | 在 Activity 里写接口请求、拼业务规则 |
| **Repository** | 数据读写 | UI |

Feature 的 `OrderListContract.View` **extends** `IBaseView`。

```java
public interface OrderListContract {
    interface View extends IBaseView {
        void showList(List<Order> orders);
        void showEmpty();
    }

    interface Presenter {
        void load();
        void onRefresh();
    }
}
```

命名：`XxxContract` / `XxxPresenter`；页面仍 `XxxActivity` / `XxxFragment` / `XxxDialog`。

---

## 四、生命周期

- `onCreate` / `onViewCreated`：`presenter.attach(this)`
- `onDestroy` / `onDestroyView`：`presenter.detach()`，Presenter 内 View 置空
- 回调里先 `isAttached()`，detach 后禁止再调 View
- Presenter **禁止** 把 View 写成强引用字段却不 detach（泄漏）

---

## 五、何时可以没有 Presenter

按当场判断，不写空 Presenter 堆文件。

| 情况 | 落点 |
|---|---|
| 有请求、状态、校验、跨控件协作 | Contract + Presenter |
| 纯展示 / 静态协议 / 关于页 | 继承业务 Base 即可，不造 Presenter |
| 确认框、单按钮提示 | `BaseDialog` 直接用 |
| 复杂 Dialog（表单、列表、多次请求） | Dialog 也走 Contract |

本轮为赶时间把逻辑写在了 Activity：做完后按「团队基础库缺口回流」事后提问这页要不要补 Presenter。不阻塞本轮。

---

## 六、检查清单

| 检查项 | 严重 |
|---|---|
| 新页面直接继承 `AppCompatActivity` / 原生 Fragment / 裸 Dialog（已有业务 Base） | 高 |
| 有请求的页在 Activity 里写接口 / 拼业务，无 Presenter | 高 |
| Presenter 持有 Activity / Context / 控件，或 `onDestroy` 不 detach | 高 |
| View 接口暴露 `TextView` 等控件 | 高 |
| 业务 Base 里出现某 Feature 方法（上帝类） | 高 |
| Foundation 里放本产品 BaseActivity | 高 |
| 全局 `presenters/` / `contracts/` 包（未按功能聚合） | 中 |
| 静态页 / 确认框硬造空 Presenter | 中 |
| 引入 Mosby / Moxy / Nucleus | 高 |
