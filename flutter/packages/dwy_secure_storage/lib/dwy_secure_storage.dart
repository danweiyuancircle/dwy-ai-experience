library;

import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// An immutable product/account scope backed by the platform credential store.
/// Initialize Flutter bindings first and configure platform entitlements/backups.
/// Hosts may inject a plugin instance with explicit access/biometric policies.
/// Serialize account logout with writes: scoped clearing is not a transaction.
final class DwySecureStorage {
  DwySecureStorage({
    required String product,
    required String account,
    FlutterSecureStorage? storage,
  }) : _prefix = 'dwy.secrets.v1.${_segment(product)}.${_segment(account)}.',
       _storage = storage ?? const FlutterSecureStorage();

  final String _prefix;
  final FlutterSecureStorage _storage;

  /// Reads one secret; missing values remain null and locked-store errors propagate.
  Future<String?> read(String key) =>
      _storage.read(key: _prefix + _segment(key));

  /// Stores a secret with the plugin's configured platform encryption policy.
  Future<void> write(String key, String value) =>
      _storage.write(key: _prefix + _segment(key), value: value);

  /// Removes one secret from this product/account only.
  Future<void> remove(String key) =>
      _storage.delete(key: _prefix + _segment(key));

  /// Deletes only this scope, never calling plugin-wide deleteAll.
  /// Partial deletion is possible on a platform error; the error is not suppressed.
  Future<void> clear() async {
    final values = await _storage.readAll();
    for (final key in values.keys.where((key) => key.startsWith(_prefix))) {
      await _storage.delete(key: key);
    }
  }
}

String _segment(String value) {
  if (value.trim().isEmpty || value.runes.any((r) => r < 32 || r == 127)) {
    throw ArgumentError(
      'A nonempty scope/key without control characters is required',
    );
  }
  return base64Url.encode(utf8.encode(value)).replaceAll('=', '');
}
