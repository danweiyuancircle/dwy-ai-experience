import 'package:dwy_component_gallery/features/gallery/image_examples.dart';
import 'package:dwy_design/dwy_design.dart';
import 'package:dwy_image/dwy_image.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'image examples default to local sources and repair decode failure',
    (tester) async {
      await tester.pumpWidget(host());
      await tester.pumpAndSettle();
      expect(find.byType(DwyImage), findsNWidgets(3));
      expect(find.text('网络图片尚未加载'), findsOneWidget);
      await tester.ensureVisible(find.text('重试解码'));
      await tester.tap(find.text('重试解码'));
      await tester.pumpAndSettle();
      expect(find.text('示例数据暂不可解码'), findsOneWidget);
      await tester.ensureVisible(find.text('修复演示数据'));
      await tester.tap(find.text('修复演示数据'));
      await tester.pumpAndSettle();
      expect(find.text('示例数据暂不可解码'), findsNothing);
      expect(find.text('已换成有效图片'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('network example rejects invalid URI before creating a cache', (
    tester,
  ) async {
    await tester.pumpWidget(host());
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('image-url')));
    await tester.enterText(
      find.byType(TextFormField),
      'file:///private/image.png',
    );
    await tester.ensureVisible(find.text('加载网络图片'));
    await tester.tap(find.text('加载网络图片'));
    await tester.pump();
    expect(find.text('请输入不含账户信息和片段的完整 HTTP(S) 图片地址。'), findsOneWidget);
    expect(find.byType(DwyImage), findsNWidgets(3));
    await tester.ensureVisible(find.text('清理当前 scope'));
    await tester.tap(find.text('清理当前 scope'));
    await tester.pump();
    expect(find.text('当前 scope 尚未创建网络缓存。'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('image controls wrap in a narrow large-text viewport', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(host(textScale: 2));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });
}

Widget host({double textScale = 1}) => MaterialApp(
  theme: DwyTheme.create(brightness: Brightness.light),
  home: Scaffold(
    body: MediaQuery(
      data: MediaQueryData(textScaler: TextScaler.linear(textScale)),
      child: const SingleChildScrollView(
        child: Padding(padding: EdgeInsets.all(24), child: ImageExamples()),
      ),
    ),
  ),
);
