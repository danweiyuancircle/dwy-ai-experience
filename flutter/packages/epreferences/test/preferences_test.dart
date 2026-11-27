import 'package:dwy_preferences/dwy_preferences.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  late _MemoryPreferences backend;
  late DwyPreferences preferences;

  setUp(() {
    backend = _MemoryPreferences();
    preferences = DwyPreferences(product: 'example', preferences: backend);
  });

  test('typed keys round trip and missing values stay absent', () async {
    final enabled = DwyPreferenceKey.boolean('enabled');
    final count = DwyPreferenceKey.integer('count');
    final ratio = DwyPreferenceKey.decimal('ratio');
    final name = DwyPreferenceKey.string('name');
    final tags = DwyPreferenceKey.stringList('tags');
    expect(await preferences.read(enabled), isNull);
    await preferences.write(enabled, true);
    await preferences.write(count, 3);
    await preferences.write(ratio, 0.5);
    await preferences.write(name, '设备');
    final source = ['one'];
    await preferences.write(tags, source);
    source.add('two');
    expect(await preferences.read(enabled), true);
    expect(await preferences.read(count), 3);
    expect(await preferences.read(ratio), 0.5);
    expect(await preferences.read(name), '设备');
    expect(await preferences.read(tags), ['one']);
    final stored = await preferences.read(tags);
    expect(() => stored!.add('three'), throwsUnsupportedError);
    await preferences.remove(count);
    expect(await preferences.read(count), isNull);
  });

  test(
    'clear only removes keys belonging to exact product and scope',
    () async {
      final other = DwyPreferences(
        product: 'example',
        scope: 'other',
        preferences: backend,
      );
      final product = DwyPreferences(
        product: 'example-other',
        preferences: backend,
      );
      final key = DwyPreferenceKey.string('language');
      await preferences.write(key, 'zh');
      await other.write(key, 'en');
      await product.write(key, 'ja');
      backend.values['native.setting'] = true;
      await preferences.clear();
      expect(await preferences.read(key), isNull);
      expect(await other.read(key), 'en');
      expect(await product.read(key), 'ja');
      expect(backend.values['native.setting'], true);
      expect(backend.lastAllowList, hasLength(1));
    },
  );

  test('reads observe backend changes instead of a private cache', () async {
    final key = DwyPreferenceKey.integer('count');
    await preferences.write(key, 1);
    backend.values[backend.values.keys.single] = 2;
    expect(await preferences.read(key), 2);
  });

  test(
    'scope separators do not collide and wrong stored types are rejected',
    () async {
      final first = DwyPreferences(
        product: 'a.b',
        scope: 'c',
        preferences: backend,
      );
      final second = DwyPreferences(
        product: 'a',
        scope: 'b.c',
        preferences: backend,
      );
      final text = DwyPreferenceKey.string('value');
      await first.write(text, 'first');
      await second.write(text, 'second');
      expect(await first.read(text), 'first');
      expect(await second.read(text), 'second');
      await expectLater(
        first.read(DwyPreferenceKey.integer('value')),
        throwsA(isA<TypeError>()),
      );
    },
  );

  test(
    'backend failures propagate and invalid keys fail before a write',
    () async {
      expect(
        () => DwyPreferences(product: '', preferences: backend),
        throwsArgumentError,
      );
      expect(() => DwyPreferenceKey.string(''), throwsArgumentError);
      backend.failure = StateError('disk unavailable');
      await expectLater(
        preferences.write(DwyPreferenceKey.boolean('x'), true),
        throwsStateError,
      );
    },
  );
}

// This test double records calls and injects failures; it does not share plugin state.
// ignore: must_be_immutable
class _MemoryPreferences extends Fake implements SharedPreferencesAsync {
  final Map<String, Object> values = {};
  Set<String>? lastAllowList;
  Object? failure;

  Future<void> _set(String key, Object value) async {
    if (failure case final error?) throw error;
    values[key] = value;
  }

  @override
  Future<bool?> getBool(String key) async => values[key] as bool?;
  @override
  Future<int?> getInt(String key) async => values[key] as int?;
  @override
  Future<double?> getDouble(String key) async => values[key] as double?;
  @override
  Future<String?> getString(String key) async => values[key] as String?;
  @override
  Future<List<String>?> getStringList(String key) async =>
      values[key] as List<String>?;
  @override
  Future<void> setBool(String key, bool value) => _set(key, value);
  @override
  Future<void> setInt(String key, int value) => _set(key, value);
  @override
  Future<void> setDouble(String key, double value) => _set(key, value);
  @override
  Future<void> setString(String key, String value) => _set(key, value);
  @override
  Future<void> setStringList(String key, List<String> value) =>
      _set(key, value);
  @override
  Future<void> remove(String key) async {
    values.remove(key);
  }

  @override
  Future<Set<String>> getKeys({Set<String>? allowList}) async => values.keys
      .where((key) => allowList == null || allowList.contains(key))
      .toSet();
  @override
  Future<void> clear({Set<String>? allowList}) async {
    lastAllowList = allowList;
    if (allowList == null) throw StateError('unscoped clear is forbidden');
    for (final key in allowList) {
      values.remove(key);
    }
  }
}
