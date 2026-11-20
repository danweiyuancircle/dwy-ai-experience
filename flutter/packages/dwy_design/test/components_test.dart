import 'package:dwy_design/dwy_design.dart';
import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('uses Cupertino controls and applies shared geometry', (
    tester,
  ) async {
    await tester.pumpWidget(
      host(
        DwyTheme.withTokens(
          tokens: const DwyTokens(controlRadius: 24),
          child: DwySettingsGroup(
            children: [
              const DwySettingsTile(title: 'Setting', subtitle: 'Details'),
              DwyButton(label: 'Continue', onPressed: () {}),
            ],
          ),
        ),
      ),
    );
    expect(find.byType(CupertinoListSection), findsOneWidget);
    expect(find.byType(CupertinoListTile), findsOneWidget);
    final button = tester.widget<CupertinoButton>(find.byType(CupertinoButton));
    expect(button.borderRadius, BorderRadius.circular(24));
    expect(button.minimumSize!.height, 48);
  });

  testWidgets(
    'loading button blocks actions and retains its accessible label',
    (tester) async {
      var calls = 0;
      await tester.pumpWidget(
        host(DwyButton(label: 'Save', loading: true, onPressed: () => calls++)),
      );
      await tester.tap(find.text('Save'));
      expect(calls, 0);
      expect(find.byType(CupertinoActivityIndicator), findsOneWidget);
      expect(find.text('Save'), findsOneWidget);
      await tester.pumpWidget(
        host(DwyButton(label: 'Save', onPressed: () => calls++)),
      );
      await tester.tap(find.text('Save'));
      expect(calls, 1);
    },
  );

  testWidgets('search clear updates controller and parent callback', (
    tester,
  ) async {
    final controller = TextEditingController(text: 'sample');
    addTearDown(controller.dispose);
    String? query;
    await tester.pumpWidget(
      host(
        DwySearchField(
          controller: controller,
          hintText: 'Search',
          clearLabel: 'Clear search',
          onChanged: (value) => query = value,
        ),
      ),
    );
    expect(find.byType(CupertinoSearchTextField), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('Clear search'));
    await tester.pump();
    expect(controller.text, isEmpty);
    expect(query, '');
    expect(find.bySemanticsLabel('Clear search'), findsNothing);
  });

  testWidgets(
    'input exposes form validation without owning application rules',
    (tester) async {
      final form = GlobalKey<FormState>();
      final controller = TextEditingController();
      addTearDown(controller.dispose);
      await tester.pumpWidget(
        host(
          Form(
            key: form,
            child: DwyTextField(
              controller: controller,
              label: 'Name',
              autofillHints: const [AutofillHints.name],
              maxLength: 7,
              validator: (value) => value!.isEmpty ? 'Required' : null,
            ),
          ),
        ),
      );
      expect(form.currentState!.validate(), isFalse);
      await tester.pump();
      expect(find.text('Required'), findsOneWidget);
      final input = find.byType(CupertinoTextField);
      expect(tester.widget<CupertinoTextField>(input).autofillHints, [
        AutofillHints.name,
      ]);
      await tester.enterText(input, 'Example overflow');
      expect(controller.text, 'Example');
      expect(form.currentState!.validate(), isTrue);
    },
  );

  testWidgets('disabled settings row also blocks its trailing control', (
    tester,
  ) async {
    var changed = false;
    await tester.pumpWidget(
      host(
        DwySettingsTile(
          title: 'Disabled setting',
          enabled: false,
          trailing: CupertinoSwitch(
            value: false,
            onChanged: (_) => changed = true,
          ),
        ),
      ),
    );
    await tester.tap(find.byType(CupertinoSwitch), warnIfMissed: false);
    expect(changed, isFalse);
  });

  testWidgets(
    'confirmation returns explicit choice; dismiss is not acceptance',
    (tester) async {
      bool? result;
      await tester.pumpWidget(
        host(
          Builder(
            builder: (context) {
              return DwyButton(
                label: 'Open',
                onPressed: () async {
                  result = await showDwyConfirmation(
                    context: context,
                    title: 'Remove item?',
                    message: 'This action needs confirmation.',
                    confirmLabel: 'Remove',
                    cancelLabel: 'Cancel',
                    destructive: true,
                  );
                },
              );
            },
          ),
        ),
      );
      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();
      expect(result, isFalse);
      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Remove'));
      await tester.pumpAndSettle();
      expect(result, isTrue);
      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();
      await tester.tapAt(const Offset(10, 10));
      await tester.pumpAndSettle();
      expect(result, isFalse);
    },
  );

  testWidgets('bottom sheet scrolls content and returns the explicit result', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetViewInsets);
    String? result;
    await tester.pumpWidget(
      host(
        Builder(
          builder: (context) {
            return DwyButton(
              label: 'Open sheet',
              onPressed: () async {
                result = await showDwySheet<String>(
                  context: context,
                  title: 'Actions',
                  builder: (sheetContext) => Column(
                    children: [
                      for (var index = 0; index < 30; index++)
                        Padding(
                          padding: const EdgeInsets.all(8),
                          child: Text('Row $index'),
                        ),
                      DwyButton(
                        label: 'Choose',
                        onPressed: () =>
                            Navigator.of(sheetContext).pop('chosen'),
                      ),
                    ],
                  ),
                );
              },
            );
          },
        ),
      ),
    );
    await tester.tap(find.text('Open sheet'));
    await tester.pumpAndSettle();
    tester.view.viewInsets = const FakeViewPadding(bottom: 300);
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Choose'));
    await tester.pumpAndSettle();
    expect(tester.getBottomRight(find.text('Choose')).dy, lessThan(544));
    await tester.tap(find.text('Choose'));
    await tester.pumpAndSettle();
    expect(result, 'chosen');
    expect(tester.takeException(), isNull);
  });

  testWidgets('settings and status fit a narrow screen with large text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      host(
        MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(2)),
          child: SingleChildScrollView(
            child: Column(
              children: [
                DwySettingsGroup(
                  title: 'Preferences',
                  children: [
                    DwySettingsTile(
                      title: 'A setting with a deliberately long title',
                      subtitle:
                          'A description that must wrap without clipping.',
                      leading: const Icon(CupertinoIcons.slider_horizontal_3),
                      trailing: CupertinoSwitch(value: true, onChanged: (_) {}),
                    ),
                  ],
                ),
                DwyStatusView(
                  title: 'Nothing to show',
                  message:
                      'Try updating this list or changing the search query.',
                  action: DwyButton(label: 'Try again', onPressed: () {}),
                ),
              ],
            ),
          ),
        ),
      ),
    );
    await tester.pump();
    expect(tester.takeException(), isNull);
  });
}

Widget host(Widget child) => CupertinoApp(
  theme: DwyTheme.create(brightness: Brightness.light),
  home: CupertinoPageScaffold(child: SafeArea(child: child)),
);
