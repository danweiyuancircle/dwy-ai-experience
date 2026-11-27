import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Widget home) => CupertinoApp(
  theme: DwyTheme.create(),
  builder: (context, child) => DwyGlass.wrap(child: child!),
  home: home,
);

void main() {
  testWidgets('glass bar actions keep their accessible label and callback', (
    tester,
  ) async {
    var taps = 0;
    await tester.pumpWidget(
      _app(
        DwyScaffold(
          title: const Text('Title'),
          trailing: DwyBarAction(
            icon: CupertinoIcons.add,
            label: 'Add item',
            onPressed: () => taps++,
          ),
          body: const SizedBox.expand(),
        ),
      ),
    );
    expect(find.text('Title'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('Add item'));
    expect(taps, 1);
    expect(tester.takeException(), isNull);
  });

  testWidgets('body sees top padding that includes the glass bar', (
    tester,
  ) async {
    double? bodyTop;
    await tester.pumpWidget(
      _app(
        DwyScaffold(
          title: const Text('Title'),
          body: Builder(
            builder: (context) {
              bodyTop = MediaQuery.paddingOf(context).top;
              return const SizedBox.expand();
            },
          ),
        ),
      ),
    );
    expect(bodyTop, greaterThanOrEqualTo(44));
  });

  testWidgets('scaffold without bar items adds no top padding', (tester) async {
    double? bodyTop;
    await tester.pumpWidget(
      _app(
        DwyScaffold(
          body: Builder(
            builder: (context) {
              bodyTop = MediaQuery.paddingOf(context).top;
              return const SizedBox.expand();
            },
          ),
        ),
      ),
    );
    expect(bodyTop, 0);
  });
}
