import 'package:dwy_component_gallery/app/gallery_app.dart';
import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('theme preview shares selection between controls', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const GalleryApp());
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

  testWidgets('desktop gallery changes theme and exercises button state', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const GalleryApp());
    await tester.tap(find.bySemanticsLabel('外观模式'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('深色'));
    await tester.pumpAndSettle();
    final app = tester.widget<CupertinoApp>(find.byType(CupertinoApp));
    expect(app.theme!.brightness, Brightness.dark);
    await tester.tap(find.text('按钮').first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('主要操作'));
    await tester.pump();
    expect(find.text('已点击 1 次'), findsOneWidget);
    await tester.tap(find.text('演示异步操作'));
    await tester.pump();
    await tester.tap(find.text('演示异步操作'));
    await tester.pump(const Duration(seconds: 1));
    await tester.pumpAndSettle();
    expect(find.text('演示操作完成'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'phone directory sheet exposes form validation and a clearable search',
    (tester) async {
      tester.view.physicalSize = const Size(390, 1100);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(const GalleryApp());
      await tester.tap(find.bySemanticsLabel('组件目录'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('输入与搜索'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('验证输入'));
      await tester.pump();
      expect(find.text('名称不能为空'), findsOneWidget);
      await tester.enterText(find.byType(CupertinoTextField).first, '示例');
      await tester.tap(find.text('验证输入'));
      await tester.pump();
      expect(find.text('输入有效：示例'), findsOneWidget);
      final search = find.byType(CupertinoTextField).last;
      await tester.ensureVisible(search);
      await tester.enterText(search, '弹窗');
      await tester.pump();
      expect(find.text('设置行'), findsNothing);
      await tester.tap(find.bySemanticsLabel('清除搜索'));
      await tester.pump();
      expect(find.text('设置行'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
