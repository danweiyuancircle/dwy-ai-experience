library;

import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';

/// Owns one product-defined Drift database and its background SQLite isolate.
/// Native platforms only. App assembly chooses the product/account-specific file;
/// schemas, DAOs and migrations belong to the product. Do not share this handle
/// across isolates, and stop/await operations before awaiting close on logout/exit.
final class DwyDatabase<DB extends GeneratedDatabase> {
  DwyDatabase._(this._database);

  final DB _database;
  Future<void>? _closing;

  /// Creates the parent directory, opens SQLite off the UI isolate and executes
  /// product migrations before returning. No destructive migration fallback exists.
  static Future<DwyDatabase<T>> open<T extends GeneratedDatabase>({
    required File file,
    required T Function(QueryExecutor executor) create,
  }) async {
    await file.parent.create(recursive: true);
    final executor = NativeDatabase.createInBackground(file);
    T? database;
    try {
      database = create(executor);
      await database.customSelect('SELECT 1').get();
      return DwyDatabase._(database);
    } catch (operation, stack) {
      try {
        if (database == null) {
          await executor.close();
        } else {
          await database.close();
        }
      } catch (cleanup) {
        throw DwyDatabaseOpenFailure(operation: operation, cleanup: cleanup);
      }
      Error.throwWithStackTrace(operation, stack);
    }
  }

  /// The typed product database; rejects new access once closing begins.
  /// Captured references still obey Drift's lifecycle and must not outlive this owner.
  DB get database {
    if (_closing != null) throw StateError('Database is closing or closed');
    return _database;
  }

  /// Delegates atomicity and rollback to Drift; errors remain visible to the caller.
  Future<T> transaction<T>(Future<T> Function(DB database) action) =>
      database.transaction(() => action(database));

  /// Closes once; repeated calls await the same result, including cleanup failures.
  Future<void> close() => _closing ??= _database.close();
}

/// Retains both failures when opening/migration and resource cleanup fail.
/// Contains original objects for diagnostics; do not expose their text to users.
final class DwyDatabaseOpenFailure implements Exception {
  DwyDatabaseOpenFailure({required this.operation, required this.cleanup});
  final Object operation;
  final Object cleanup;
  @override
  String toString() => 'Database open and cleanup failed';
}
