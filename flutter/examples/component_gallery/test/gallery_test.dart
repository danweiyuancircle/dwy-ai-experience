import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_component_gallery/app/gallery_app.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> _pumpGallery(WidgetTester tester, Size size) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  await tester.pumpWidget(const GalleryApp());
}

Finder _entry(String id) => find.byKey(Key('catalog-$id'));

void main() {
  testWidgets('theme preview shares selection between controls', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(1440, 1400));
    final segment = find.descendant(
      of: find.byType(CupertinoSlidingSegmentedControl<int>),
      matching: find.text('记录'),
    );
    await tester.ensureVisible(segment);
    await tester.tap(segment);
    await tester.pumpAndSettle();
    expect(
      tester.widget<CupertinoTabBar>(find.byType(CupertinoTabBar)).currentIndex,
      1,
    );
    final home = find.descendant(
      of: find.byType(CupertinoTabBar),
      matching: find.text('概览'),
    );
    await tester.tap(home);
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<CupertinoSlidingSegmentedControl<int>>(
            find.byType(CupertinoSlidingSegmentedControl<int>),
          )
          .groupValue,
      0,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('brand color switch updates the app theme', (tester) async {
    await _pumpGallery(tester, const Size(1440, 1400));
    final before = tester
        .widget<CupertinoApp>(find.byType(CupertinoApp))
        .theme!
        .primaryColor;
    await tester.ensureVisible(find.text('松石绿'));
    await tester.tap(find.text('松石绿'));
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<CupertinoApp>(find.byType(CupertinoApp))
          .theme!
          .primaryColor,
      isNot(before),
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('desktop gallery changes theme and exercises button state', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(1440, 1100));
    await tester.tap(find.bySemanticsLabel('外观模式'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('深色'));
    await tester.pumpAndSettle();
    final app = tester.widget<CupertinoApp>(find.byType(CupertinoApp));
    expect(app.theme!.brightness, Brightness.dark);
    await tester.tap(_entry('button'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('主要操作'));
    await tester.pump();
    expect(find.text('已点击 1 次'), findsOneWidget);
    await tester.tap(find.text('重置示例'));
    await tester.pump();
    expect(find.text('已点击 0 次'), findsOneWidget);
    await tester.tap(find.text('演示异步操作'));
    await tester.pump();
    await tester.tap(find.text('演示异步操作'));
    await tester.pump(const Duration(seconds: 1));
    await tester.pumpAndSettle();
    expect(find.text('演示操作完成'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('state selector switches the displayed status view', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(1440, 1100));
    await tester.tap(_entry('status'));
    await tester.pumpAndSettle();
    expect(find.text('这里还没有内容'), findsOneWidget);
    await tester.tap(find.text('错误'));
    await tester.pumpAndSettle();
    expect(find.text('暂时无法获取内容'), findsOneWidget);
    await tester.tap(find.text('重试演示'));
    await tester.pump();
    expect(find.text('已触发重试 1 次'), findsOneWidget);
    await tester.tap(find.text('重置示例'));
    await tester.pump();
    expect(find.text('已触发重试 1 次'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('catalog search filters entries and reports no match', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(1440, 1100));
    final search = find.byType(CupertinoSearchTextField);
    await tester.enterText(search, 'status');
    await tester.pump();
    expect(_entry('status'), findsOneWidget);
    expect(_entry('button'), findsNothing);
    await tester.enterText(search, 'zzz-none');
    await tester.pump();
    expect(find.text('没有匹配的组件'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('component detail lists capabilities, constraints and code', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(1440, 1100));
    await tester.tap(_entry('button'));
    await tester.pumpAndSettle();
    expect(find.text('支持的能力'), findsOneWidget);
    expect(find.text('用法与约束'), findsOneWidget);
    expect(find.text('Dart 示例'), findsOneWidget);
    expect(find.text('复制示例'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'phone directory sheet exposes form validation and a clearable search',
    (tester) async {
      await _pumpGallery(tester, const Size(390, 1100));
      await tester.tap(find.bySemanticsLabel('组件目录'));
      await tester.pumpAndSettle();
      await tester.tap(_entry('text-field'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('验证输入'));
      await tester.pump();
      expect(find.text('名称不能为空'), findsOneWidget);
      await tester.enterText(find.byType(CupertinoTextField).first, '示例');
      await tester.tap(find.text('验证输入'));
      await tester.pump();
      expect(find.text('输入有效：示例'), findsOneWidget);
      await tester.tap(find.bySemanticsLabel('组件目录'));
      await tester.pumpAndSettle();
      await tester.tap(_entry('search-field'));
      await tester.pumpAndSettle();
      final search = find.byType(CupertinoTextField).first;
      await tester.ensureVisible(search);
      await tester.enterText(search, '弹窗');
      await tester.pumpAndSettle();
      expect(find.text('设置行'), findsNothing);
      await tester.tap(find.byIcon(CupertinoIcons.xmark_circle_fill).first);
      await tester.pump();
      expect(find.text('设置行'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('glass navigation entry explains limits and opens the demo', (
    tester,
  ) async {
    await _pumpGallery(tester, const Size(390, 1100));
    await tester.tap(find.bySemanticsLabel('组件目录'));
    await tester.pumpAndSettle();
    await tester.tap(_entry('scaffold'));
    await tester.pumpAndSettle();
    expect(find.textContaining('纯色背景看不出折射'), findsOneWidget);
    await tester.ensureVisible(find.text('打开玻璃导航栏示例'));
    await tester.tap(find.text('打开玻璃导航栏示例'));
    await tester.pumpAndSettle();
    expect(find.text('玻璃导航栏示例'), findsOneWidget);
    expect(
      tester.getTopLeft(find.text('色块 1')).dy,
      greaterThanOrEqualTo(44),
      reason: '首个色块不能被导航栏盖住',
    );
    await tester.tap(find.bySemanticsLabel('返回'));
    await tester.pumpAndSettle();
    expect(find.text('打开玻璃导航栏示例'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
