import 'package:cupertino_ui/cupertino_ui.dart';

import '../features/gallery/examples/button_example.dart';
import '../features/gallery/examples/glass_example.dart';
import '../features/gallery/examples/input_examples.dart';
import '../features/gallery/examples/overlay_examples.dart';
import '../features/gallery/examples/settings_status_examples.dart';
import '../features/gallery/examples/theme_example.dart';
import '../features/gallery/image_examples.dart';
import 'entry.dart';

/// Every public export of dwy_design and dwy_image must appear in some entry's
/// `symbols`; catalog_test.dart enforces this against the package barrels.
final List<CatalogEntry> galleryCatalog = [
  CatalogEntry(
    id: 'theme',
    name: 'DwyTheme',
    title: '主题与令牌',
    category: GalleryCategory.foundation,
    package: 'dwy_design',
    icon: CupertinoIcons.paintbrush,
    summary: '品牌色、浅深色、圆角与间距令牌的统一入口；应用声明一次，页面和弹层共用。',
    symbols: ['DwyTheme', 'DwyBrand', 'DwyTokens'],
    capabilities: [
      'DwyTheme.create 返回独立 cupertino_ui 的 CupertinoThemeData，省略 brightness 时跟随系统',
      'DwyBrand 声明主色与字体，按钮、Tab 选中态同步更新',
      'DwyTokens：controlRadius、groupRadius、controlHeight、pageInset 与固定间距 spaceXS 至 spaceXL',
      'DwyTheme.withTokens 在根应用 builder 中注入令牌，页面与弹层用 DwyTheme.tokensOf 读取',
      '单个按钮可用 DwyButton.padding 覆盖内边距（组件级定制）',
    ],
    constraints: [
      'withTokens 必须放在 CupertinoApp.builder，否则弹层读不到覆盖值',
      'controlHeight 不得小于 48（点击区域底线）',
      '文字缩放始终开启，不在令牌中关闭',
    ],
    code: r'''
CupertinoApp(
  theme: DwyTheme.create(
    brand: const DwyBrand(primary: Color(0xFF2563EB)),
  ),
  builder: (context, child) => DwyTheme.withTokens(
    tokens: const DwyTokens(controlRadius: 24),
    child: child!,
  ),
  home: const HomePage(),
);''',
    builder: (context, state) => const ThemeExample(),
  ),
  CatalogEntry(
    id: 'button',
    name: 'DwyButton',
    title: '按钮',
    category: GalleryCategory.actions,
    package: 'dwy_design',
    icon: CupertinoIcons.add_circled,
    summary: '四种层级的操作按钮，加载时保留标签并阻止重复触发。',
    symbols: ['DwyButton', 'DwyButtonVariant'],
    capabilities: [
      'DwyButtonVariant：primary、secondary、subtle、danger',
      'loading：显示指示器、保留文字、忽略点击',
      'onPressed 为 null 时禁用',
      '可选 icon；最小高度跟随 DwyTokens.controlHeight，圆角跟随 controlRadius',
      'padding 覆盖单个按钮的内边距',
    ],
    constraints: [
      '异步操作由调用方持有，结束后必须把 loading 置回 false',
      'icon 仅用于辅助识别，标签文字不可省略',
    ],
    code: r'''
DwyButton(
  label: '保存',
  icon: CupertinoIcons.check_mark,
  variant: DwyButtonVariant.primary,
  loading: saving,
  onPressed: save,
);''',
    states: const [
      ExampleState('default', '默认'),
      ExampleState('loading', '加载中'),
      ExampleState('disabled', '禁用'),
    ],
    builder: (context, state) => ButtonExample(state: state),
  ),
  CatalogEntry(
    id: 'text-field',
    name: 'DwyTextField',
    title: '输入框',
    category: GalleryCategory.input,
    package: 'dwy_design',
    icon: CupertinoIcons.textbox,
    summary: '带标签、说明、错误和清除动作的受控表单输入。',
    symbols: ['DwyTextField'],
    capabilities: [
      'label、hintText、helperText、errorText 与 Form validator',
      'clearLabel 提供无障碍的清除按钮',
      'maxLength、autofillHints、keyboardType、textInputAction',
      'prefixIcon、obscureText、多行输入（obscureText 时仅单行）',
      '表单 reset 时恢复初始文本',
    ],
    constraints: ['调用方创建并释放 controller 与 focusNode', '校验规则和本地化文案由业务层提供'],
    code: r'''
DwyTextField(
  controller: name,
  label: '名称',
  clearLabel: '清除名称',
  validator: (value) => value!.trim().isEmpty ? '名称不能为空' : null,
);''',
    states: const [
      ExampleState('default', '默认'),
      ExampleState('error', '外部错误'),
      ExampleState('disabled', '禁用'),
    ],
    builder: (context, state) => TextFieldExample(state: state),
  ),
  CatalogEntry(
    id: 'search-field',
    name: 'DwySearchField',
    title: '搜索框',
    category: GalleryCategory.input,
    package: 'dwy_design',
    icon: CupertinoIcons.search,
    summary: '带显式清除动作的搜索输入，只负责输入，不发起查询。',
    symbols: ['DwySearchField'],
    capabilities: [
      'onChanged / onSubmitted 回调给调用方',
      'clearLabel 作为清除图标的无障碍标签',
      '圆角跟随 DwyTokens.controlRadius',
      'enabled 控制可用性',
    ],
    constraints: ['防抖、请求和结果过滤由调用方实现', 'controller 由调用方释放'],
    code: r'''
DwySearchField(
  controller: search,
  hintText: '搜索',
  clearLabel: '清除搜索',
  onChanged: (value) => setState(() => query = value),
);''',
    states: const [
      ExampleState('default', '默认'),
      ExampleState('disabled', '禁用'),
    ],
    builder: (context, state) => SearchFieldExample(state: state),
  ),
  CatalogEntry(
    id: 'settings',
    name: 'DwySettingsGroup',
    title: '设置分组与设置行',
    category: GalleryCategory.content,
    package: 'dwy_design',
    icon: CupertinoIcons.slider_horizontal_3,
    summary: '圆角分组容器与可换行的设置行，用于列表式设置页。',
    symbols: ['DwySettingsGroup', 'DwySettingsTile'],
    capabilities: [
      'DwySettingsGroup：可选 title 与 footnote，圆角跟随 groupRadius',
      'DwySettingsTile：标题、可换行说明、leading、trailing',
      '整行 onTap 自动显示下级箭头',
      'enabled=false 同时阻止尾部控件的交互与语义',
    ],
    constraints: [
      '尾部为 Switch 等可交互控件时不要再设 onTap，避免点击竞争和重复语义',
      'children 为空时使用占位，不报错',
    ],
    code: r'''
DwySettingsGroup(
  title: '偏好',
  children: [
    DwySettingsTile(
      title: '通知',
      trailing: CupertinoSwitch(value: on, onChanged: setOn),
    ),
    DwySettingsTile(title: '关于', onTap: openAbout),
  ],
);''',
    states: const [
      ExampleState('default', '默认'),
      ExampleState('disabled', '全部禁用'),
    ],
    builder: (context, state) => SettingsExample(state: state),
  ),
  CatalogEntry(
    id: 'status',
    name: 'DwyStatusView',
    title: '内容状态',
    category: GalleryCategory.feedback,
    package: 'dwy_design',
    icon: CupertinoIcons.tray,
    summary: '空态、加载、错误的统一布局，重试动作由调用方提供。',
    symbols: ['DwyStatusView', 'DwyStatusKind'],
    capabilities: [
      'DwyStatusKind：empty、loading、error',
      'title、message、自定义 icon 与 action 插槽',
      '加载使用不确定进度指示器',
    ],
    constraints: ['kind 只描述呈现，数据状态由 Feature 持有', 'loading 不伪造进度百分比'],
    code: r'''
DwyStatusView(
  kind: DwyStatusKind.error,
  title: '暂时无法获取内容',
  message: '请稍后重试',
  action: DwyButton(label: '重试', onPressed: reload),
);''',
    states: const [
      ExampleState('empty', '空结果'),
      ExampleState('loading', '加载中'),
      ExampleState('error', '错误'),
    ],
    builder: (context, state) => StatusExample(state: state),
  ),
  CatalogEntry(
    id: 'confirmation',
    name: 'showDwyConfirmation',
    title: '确认弹窗',
    category: GalleryCategory.feedback,
    package: 'dwy_design',
    icon: CupertinoIcons.exclamationmark_triangle,
    summary: '系统风格的确认对话框，只有确认才返回 true。',
    symbols: ['showDwyConfirmation'],
    capabilities: ['destructive 切换确认按钮为危险样式', '取消、返回、点击遂罩均返回 false'],
    constraints: ['调用方 await 结果后才执行真实动作', 'await 之后使用 context 前检查 mounted'],
    code: r'''
final ok = await showDwyConfirmation(
  context: context,
  title: '删除记录？',
  message: '此操作无法撤销。',
  confirmLabel: '删除',
  cancelLabel: '取消',
  destructive: true,
);
if (ok && context.mounted) await delete();''',
    states: const [
      ExampleState('normal', '普通'),
      ExampleState('destructive', '危险'),
    ],
    builder: (context, state) => ConfirmationExample(state: state),
  ),
  CatalogEntry(
    id: 'sheet',
    name: 'showDwySheet',
    title: '底部面板',
    category: GalleryCategory.feedback,
    package: 'dwy_design',
    icon: CupertinoIcons.rectangle,
    summary: '带安全区域、键盘避让和拖拽手柄的底部面板。',
    symbols: ['showDwySheet'],
    capabilities: [
      '内容可滚动，与面板拖拽联动',
      '标题带标题语义',
      '泛型返回值：Navigator.pop(sheetContext, result)',
    ],
    constraints: ['关闭面板使用 builder 提供的 sheetContext', '下滑关闭时返回 null'],
    code: r'''
final result = await showDwySheet<String>(
  context: context,
  title: '操作',
  builder: (sheetContext) => DwyButton(
    label: '完成',
    onPressed: () => Navigator.pop(sheetContext, 'done'),
  ),
);''',
    builder: (context, state) => const SheetExample(),
  ),
  CatalogEntry(
    id: 'scaffold',
    name: 'DwyScaffold',
    title: '玻璃导航栏',
    category: GalleryCategory.navigation,
    package: 'dwy_design',
    icon: CupertinoIcons.sparkles,
    summary: '带玻璃材质导航栏的页面骨架，内容延伸到栏下方以显示折射。',
    symbols: ['DwyScaffold', 'DwyBarAction', 'DwyGlass'],
    capabilities: [
      'DwyScaffold：title、leading、trailing、可自定义 background',
      'DwyBarAction：圆形玻璃图标按钮，必须提供无障碍 label',
      'DwyGlass.initialize 预加载 shader；DwyGlass.wrap 放在 CupertinoApp.builder',
      '后端库只在 dwy_design 内部依赖，调用方不直接引用',
    ],
    constraints: [
      '纯色背景看不出折射，需传渐变或图片作为 background',
      'body 延伸到栏下方，Scaffold 只抬高 MediaQuery.padding.top；SafeArea 与未指定 padding 的 ListView 会自动避让；SingleChildScrollView 或显式指定 padding 的 ListView 需自己读取顶部内边距',
      '只有导航栏按钮玻璃化，其余控件仍是 Cupertino 控件',
      '需要 DwyGlass.wrap 在上层；该包使用的兼容桥已被上游弃用',
    ],
    code: r'''
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await DwyGlass.initialize();
  runApp(const App());
}

// CupertinoApp(builder: (context, child) => DwyGlass.wrap(child: child!))
DwyScaffold(
  title: const Text('标题'),
  trailing: DwyBarAction(
    icon: CupertinoIcons.add,
    label: '新增',
    onPressed: add,
  ),
  body: ListView(children: items),
);''',
    states: const [
      ExampleState('gradient', '渐变背景'),
      ExampleState('flat', '纯色背景'),
    ],
    builder: (context, state) => GlassExample(state: state),
  ),
  CatalogEntry(
    id: 'image',
    name: 'DwyImage',
    title: '图片',
    category: GalleryCategory.media,
    package: 'dwy_image',
    icon: CupertinoIcons.photo,
    summary: '固定尺寸图片，支持 asset、内存、文件与带作用域缓存的网络来源。',
    symbols: [
      'DwyImage',
      'DwyImageSource',
      'DwyImageCache',
      'DwyImagePlaceholderBuilder',
      'DwyImageErrorBuilder',
    ],
    capabilities: [
      'DwyImageSource.asset / memory / file / network',
      '物理解码上限 cacheWidth / cacheHeight、圆角、fit',
      '自定义加载占位与错误占位，内置重试会先清除该来源的缓存',
      'DwyImageCache：按 namespace 隔离的磁盘与内存缓存，可 clear / dispose',
    ],
    constraints: [
      '网络地址必须是不含账户信息和片段的 HTTP(S)',
      '同一 namespace 同时只能有一个活动持有者；清理前先卸载使用该缓存的图片',
      'Web 上游实现没有同等磁盘缓存，移动端缓存清理需另外验证',
      '不要向用户展示原始异常文字',
    ],
    code: r'''
final cache = DwyImageCache(namespace: 'avatar_user42');
DwyImage(
  source: DwyImageSource.network(uri, cache: cache),
  width: 96,
  height: 96,
  cacheWidth: 192,
  borderRadius: BorderRadius.circular(48),
  semanticLabel: '头像',
);''',
    builder: (context, state) => const ImageExamples(),
  ),
];
