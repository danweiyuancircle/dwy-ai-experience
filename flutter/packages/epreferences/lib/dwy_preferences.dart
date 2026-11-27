library;

import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// A typed preference declaration; use the same type for a name throughout a scope.
/// Preferences are optional settings, never credentials or durable business data.
final class DwyPreferenceKey<T extends Object> {
  DwyPreferenceKey._(this.name, this._read, this._write) {
    _validate(name, 'name');
  }

  final String name;
  final Future<T?> Function(SharedPreferencesAsync, String) _read;
  final Future<void> Function(SharedPreferencesAsync, String, T) _write;

  /// Declares a boolean setting without an implicit fallback value.
  static DwyPreferenceKey<bool> boolean(String name) => DwyPreferenceKey._(
    name,
    (s, k) => s.getBool(k),
    (s, k, v) => s.setBool(k, v),
  );

  /// Declares an integer setting.
  static DwyPreferenceKey<int> integer(String name) => DwyPreferenceKey._(
    name,
    (s, k) => s.getInt(k),
    (s, k, v) => s.setInt(k, v),
  );

  /// Declares a floating-point setting supported by platform preferences.
  static DwyPreferenceKey<double> decimal(String name) => DwyPreferenceKey._(
    name,
    (s, k) => s.getDouble(k),
    (s, k, v) => s.setDouble(k, v),
  );

  /// Declares a text setting.
  static DwyPreferenceKey<String> string(String name) => DwyPreferenceKey._(
    name,
    (s, k) => s.getString(k),
    (s, k, v) => s.setString(k, v),
  );

  /// Copies list values so mutating a caller-owned list cannot change a pending write.
  static DwyPreferenceKey<List<String>> stringList(String name) =>
      DwyPreferenceKey._(name, (s, k) async {
        final value = await s.getStringList(k);
        return value == null ? null : List<String>.unmodifiable(value);
      }, (s, k, v) => s.setStringList(k, List<String>.of(v)));
}

/// Product-scoped settings using uncached platform reads across isolates/engines.
/// Initialize Flutter bindings before using the default backend. Clearing a scope
/// is not transactional; callers must serialize it with writes during account changes.
final class DwyPreferences {
  DwyPreferences({
    required String product,
    String scope = 'app',
    SharedPreferencesAsync? preferences,
  }) : _prefix = 'dwy.preferences.v1.${_segment(product)}.${_segment(scope)}.',
       _preferences = preferences ?? SharedPreferencesAsync();

  final String _prefix;
  final SharedPreferencesAsync _preferences;

  /// Reads the current platform value; absent values remain null and type errors propagate.
  Future<T?> read<T extends Object>(DwyPreferenceKey<T> key) =>
      key._read(_preferences, _prefix + _segment(key.name));

  /// Completes when the plugin acknowledges the write, not a durable database commit.
  Future<void> write<T extends Object>(DwyPreferenceKey<T> key, T value) =>
      key._write(_preferences, _prefix + _segment(key.name), value);

  /// Removes one declared preference from this scope.
  Future<void> remove<T extends Object>(DwyPreferenceKey<T> key) =>
      _preferences.remove(_prefix + _segment(key.name));

  /// Deletes only keys observed in this exact scope, preserving native and other product keys.
  Future<void> clear() async {
    final keys = await _preferences.getKeys();
    await _preferences.clear(
      allowList: keys.where((key) => key.startsWith(_prefix)).toSet(),
    );
  }
}

String _segment(String value) {
  _validate(value, 'scope');
  return base64Url.encode(utf8.encode(value)).replaceAll('=', '');
}

void _validate(String value, String parameter) {
  if (value.trim().isEmpty || value.runes.any((r) => r < 32 || r == 127)) {
    throw ArgumentError(
      'A nonempty $parameter without control characters is required',
    );
  }
}
