import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('settings subtitle respects theme and disabled colors', (
    tester,
  ) async {
    final base = DwyTheme.create(brightness: Brightness.light);
    final theme = base.copyWith(
      listTileTheme: base.listTileTheme.copyWith(
        subtitleTextStyle: const TextStyle(
          fontSize: 19,
          color: Colors.deepPurple,
        ),
      ),
    );
    for (final enabled in [true, false]) {
      await tester.pumpWidget(
        MaterialApp(
          theme: theme,
          home: Scaffold(
            body: DwySettingsTile(
              title: 'Setting',
              subtitle: 'Details',
              enabled: enabled,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final style = DefaultTextStyle.of(tester.element(find.text('Details')))
          .style;
      expect(style.fontSize, 19);
      expect(style.color, enabled ? Colors.deepPurple : theme.disabledColor);
    }
  });

  for (final brightness in Brightness.values) {
    testWidgets('$brightness themed controls fit and retain selection', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(320, 800);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      var selected = 0;
      await tester.pumpWidget(
        MaterialApp(
          theme: DwyTheme.create(brightness: brightness),
          home: MediaQuery(
            data: const MediaQueryData(textScaler: TextScaler.linear(2)),
            child: Scaffold(
              body: StatefulBuilder(
                builder: (context, setState) => SingleChildScrollView(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Card(
                      child: Column(
                        children: [
                          const ListTile(
                            title: Text('Title'),
                            subtitle: Text('Description wraps'),
                          ),
                          SegmentedButton<int>(
                            segments: const [
                              ButtonSegment(value: 0, label: Text('One')),
                              ButtonSegment(value: 1, label: Text('Two')),
                            ],
                            selected: {selected},
                            onSelectionChanged: (values) =>
                                setState(() => selected = values.single),
                          ),
                          NavigationBar(
                            selectedIndex: selected,
                            onDestinationSelected: (value) =>
                                setState(() => selected = value),
                            destinations: const [
                              NavigationDestination(
                                icon: Icon(Icons.home_outlined),
                                label: 'Home',
                              ),
                              NavigationDestination(
                                icon: Icon(Icons.list),
                                label: 'List',
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Two'));
      await tester.pumpAndSettle();
      expect(selected, 1);
      await tester.tap(find.text('Home'));
      await tester.pumpAndSettle();
      expect(selected, 0);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets(
    'loading button blocks actions and retains its accessible label',
    (tester) async {
      var calls = 0;
      await tester.pumpWidget(
        host(DwyButton(label: 'Save', loading: true, onPressed: () => calls++)),
      );
      await tester.tap(find.text('Save'));
      expect(calls, 0);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
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
    await tester.tap(find.byTooltip('Clear search'));
    await tester.pump();
    expect(controller.text, isEmpty);
    expect(query, '');
    expect(find.byTooltip('Clear search'), findsNothing);
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
              validator: (value) => value!.isEmpty ? 'Required' : null,
            ),
          ),
        ),
      );
      expect(form.currentState!.validate(), isFalse);
      await tester.pump();
      expect(find.text('Required'), findsOneWidget);
      await tester.enterText(find.byType(TextFormField), 'Example');
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
          trailing: Switch(value: false, onChanged: (_) => changed = true),
        ),
      ),
    );
    await tester.tap(find.byType(Switch), warnIfMissed: false);
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
    await tester.ensureVisible(find.text('Choose'));
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
                      leading: const Icon(Icons.tune),
                      trailing: Switch(value: true, onChanged: (_) {}),
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

Widget host(Widget child) => MaterialApp(
  theme: DwyTheme.create(brightness: Brightness.light),
  home: Scaffold(body: SafeArea(child: child)),
);
