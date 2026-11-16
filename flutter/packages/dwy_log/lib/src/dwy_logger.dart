import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:logger/logger.dart' as backend;

/// Severity ordering used by every DWY package.
enum DwyLogLevel { debug, info, warning, error }

/// Local log policy. [directory] must be dedicated to one logger in one isolate.
/// Never point it at a general cache/user directory: owned archives are removed.
final class DwyLogConfig {
  DwyLogConfig({
    required this.directory,
    this.minimumLevel = DwyLogLevel.info,
    this.console = false,
    this.maxFileSizeKB = 2048,
    this.maxRotatedFiles = 5,
    this.retention = const Duration(days: 7),
  }) {
    if (maxFileSizeKB < 1 ||
        maxRotatedFiles < 1 ||
        retention <= Duration.zero) {
      throw ArgumentError(
        'Log size, archive count and retention must be positive.',
      );
    }
  }

  final Directory directory;
  final DwyLogLevel minimumLevel;
  final bool console;
  final int maxFileSizeKB;
  final int maxRotatedFiles;
  final Duration retention;
}

/// Category-scoped logger sharing one file writer; await [close] during shutdown.
/// Records are JSON lines. Never place secrets in free-form messages; prefer fields.
final class DwyLogger {
  DwyLogger._(this._session, this._category);
  final _LogSession _session;
  final String _category;

  /// Opens a local-only writer. No upload, Flutter engine or global singleton.
  static Future<DwyLogger> open(
    DwyLogConfig config, {
    DwyLogFileOperations? fileOperations,
  }) async {
    final session = _LogSession(
      config,
      fileOperations ?? DwyLogFileOperations(),
    );
    await session.open();
    return DwyLogger._(session, 'app');
  }

  /// Returns a category handle with the same lifecycle and severity configuration.
  DwyLogger category(String category) {
    if (category.trim().isEmpty ||
        category.contains(RegExp(r'[\x00-\x1f\x7f]'))) {
      throw ArgumentError.value(
        category,
        'category',
        'Use a nonempty diagnostic category.',
      );
    }
    return DwyLogger._(_session, category);
  }

  /// Writes a diagnostic record; credentials in structured fields are redacted.
  /// Await this operation to observe file I/O errors; use [flush] before exporting.
  Future<void> log(
    DwyLogLevel level,
    String message, {
    Map<String, Object?> fields = const {},
    Object? error,
    StackTrace? stackTrace,
  }) {
    return _session.write(level, _category, message, fields, error, stackTrace);
  }

  /// Writes a debug record when enabled by the configured threshold.
  Future<void> debug(
    String message, {
    Map<String, Object?> fields = const {},
  }) => log(DwyLogLevel.debug, message, fields: fields);

  /// Writes an informational record.
  Future<void> info(String message, {Map<String, Object?> fields = const {}}) =>
      log(DwyLogLevel.info, message, fields: fields);

  /// Writes an expected failure or warning record.
  Future<void> warning(
    String message, {
    Map<String, Object?> fields = const {},
    Object? error,
    StackTrace? stackTrace,
  }) => log(
    DwyLogLevel.warning,
    message,
    fields: fields,
    error: error,
    stackTrace: stackTrace,
  );

  /// Writes an error's type and optional stack, never its potentially sensitive text.
  Future<void> error(
    String message, {
    Map<String, Object?> fields = const {},
    Object? error,
    StackTrace? stackTrace,
  }) => log(
    DwyLogLevel.error,
    message,
    fields: fields,
    error: error,
    stackTrace: stackTrace,
  );

  /// Drains previous writes before returning; later records keep using this logger.
  Future<void> flush() => _session.flush();

  /// Creates a new snapshot directory under [parent], without overwriting files.
  /// The caller controls sharing and removes the snapshot when no longer needed.
  Future<Directory> exportTo(Directory parent) => _session.exportTo(parent);

  /// Rejects new records and drains queued work; safe to call repeatedly.
  Future<void> close() => _session.close();
}

/// File operations for controlled sinks and deterministic I/O failure tests.
/// Implementations must finish all owned work before their futures complete.
class DwyLogFileOperations {
  Future<RandomAccessFile> open(File file) => file.open(mode: FileMode.append);
  Future<void> rename(File source, File destination) async {
    await source.rename(destination.path);
  }

  Future<void> delete(File file) async {
    await file.delete();
  }
}

/// The session is terminal after an owned log-file failure; inspect [cause].
final class DwyLogUnavailable implements Exception {
  const DwyLogUnavailable(this.cause);
  final Object cause;
  @override
  String toString() => 'DwyLogUnavailable';
}

/// Preserves both a file operation failure and a subsequent cleanup failure.
final class DwyLogCleanupFailure implements Exception {
  const DwyLogCleanupFailure({required this.operation, required this.cleanup});
  final Object operation;
  final Object cleanup;
  @override
  String toString() => 'DwyLogCleanupFailure';
}

final class _LogSession {
  _LogSession(this.config, this.files);
  final DwyLogConfig config;
  final DwyLogFileOperations files;
  final _LineOutput _output = _LineOutput();
  late backend.Logger _logger;
  RandomAccessFile? _writer;
  var _fileBytes = 0;
  Future<void> _tail = Future<void>.value();
  Future<void>? _closing;
  Object? _failure;
  var _rotation = 0;

  File get _latest =>
      File('${config.directory.path}${Platform.pathSeparator}latest.log');

  Future<void> open() async {
    await config.directory.create(recursive: true);
    if (await FileSystemEntity.type(
          config.directory.path,
          followLinks: false,
        ) !=
        FileSystemEntityType.directory) {
      throw ArgumentError('Log directory cannot be a symbolic link.');
    }
    await for (final entry in config.directory.list(followLinks: false)) {
      final name = entry.uri.pathSegments.where((part) => part.isNotEmpty).last;
      if (entry is! File ||
          (name != 'latest.log' &&
              !(name.startsWith('archive_') && name.endsWith('.log')))) {
        throw ArgumentError(
          'Log directory contains unrelated files; use a dedicated directory.',
        );
      }
    }
    _logger = backend.Logger(
      filter: backend.ProductionFilter(),
      printer: _JsonPrinter(),
      output: _output,
      level: backend.Level.debug,
    );
    await _logger.init;
    try {
      await _pruneArchives();
      await _openWriter();
    } on FileSystemException catch (error) {
      try {
        await _closeWriter();
      } on FileSystemException catch (cleanup) {
        throw DwyLogCleanupFailure(operation: error, cleanup: cleanup);
      } finally {
        await _logger.close();
      }
      rethrow;
    }
  }

  Future<void> _openWriter() async {
    _writer = await files.open(_latest);
    _fileBytes = await _writer!.length();
  }

  Future<T> _enqueue<T>(FutureOr<T> Function() action) {
    if (_closing != null)
      return Future<T>.error(StateError('Logger is closed.'));
    return _append(() {
      if (_failure case final cause?) throw DwyLogUnavailable(cause);
      return action();
    });
  }

  Future<T> _append<T>(FutureOr<T> Function() action) {
    final result = _tail.then((_) => action());
    // Each caller receives its own error while close can still drain the queue.
    _tail = result.then<void>((_) {}, onError: (Object _, StackTrace __) {});
    return result;
  }

  Future<T> _owned<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on FileSystemException catch (error) {
      _failure ??= error;
      rethrow;
    } on DwyLogCleanupFailure catch (error) {
      _failure ??= error;
      rethrow;
    }
  }

  Future<void> write(
    DwyLogLevel level,
    String category,
    String message,
    Map<String, Object?> fields,
    Object? error,
    StackTrace? stackTrace,
  ) {
    final record = <String, Object?>{
      'time': DateTime.now().toUtc().toIso8601String(),
      'level': level.name,
      'category': _redactText(category),
      'message': _redactText(message),
      if (fields.isNotEmpty) 'fields': _redactValue(fields),
      if (error != null) 'error_type': error.runtimeType.toString(),
      if (stackTrace != null) 'stack': _redactText(stackTrace.toString()),
    };
    return _enqueue(() async {
      if (level.index < config.minimumLevel.index) return;
      _logger.log(switch (level) {
        DwyLogLevel.debug => backend.Level.debug,
        DwyLogLevel.info => backend.Level.info,
        DwyLogLevel.warning => backend.Level.warning,
        DwyLogLevel.error => backend.Level.error,
      }, record);
      final bytes = utf8.encode('${_output.take().join('\n')}\n');
      await _owned(() async {
        if (_fileBytes > 0 &&
            _fileBytes + bytes.length > config.maxFileSizeKB * 1024) {
          await _closeWriter();
          await files.rename(
            _latest,
            File(
              '${config.directory.path}${Platform.pathSeparator}archive_${DateTime.now().microsecondsSinceEpoch}_${_rotation++}.log',
            ),
          );
          await _openWriter();
          await _pruneArchives();
        }
        await _writer!.writeFrom(bytes);
        _fileBytes += bytes.length;
      });
      if (config.console) stdout.write(utf8.decode(bytes));
    });
  }

  Future<void> flush() => _enqueue(
    () => _owned(() async {
      await _writer!.flush();
      await _pruneArchives();
    }),
  );

  Future<Directory> exportTo(Directory parent) => _enqueue(() async {
    final root = await config.directory.resolveSymbolicLinks();
    final target = await parent.resolveSymbolicLinks();
    final comparableRoot = Platform.isWindows ? root.toLowerCase() : root;
    final comparableTarget = Platform.isWindows ? target.toLowerCase() : target;
    if (comparableTarget == comparableRoot ||
        comparableTarget.startsWith(
          '$comparableRoot${Platform.pathSeparator}',
        )) {
      throw ArgumentError('Export outside the managed log directory.');
    }
    await _owned(() async {
      await _writer!.flush();
      await _pruneArchives();
    });
    final snapshot = await parent.createTemp('dwy-logs-');
    try {
      await for (final file in config.directory.list(followLinks: false)) {
        if (file is File) {
          await file.copy(
            '${snapshot.path}${Platform.pathSeparator}${file.uri.pathSegments.last}',
          );
        }
      }
      return snapshot;
    } on FileSystemException catch (error) {
      try {
        await snapshot.delete(recursive: true);
      } on FileSystemException catch (cleanup) {
        throw DwyLogCleanupFailure(operation: error, cleanup: cleanup);
      }
      rethrow;
    }
  });

  Future<void> _pruneArchives() async {
    final cutoff = DateTime.now().subtract(config.retention);
    final retained = <(File, DateTime)>[];
    await for (final entry in config.directory.list(followLinks: false)) {
      final name = entry.uri.pathSegments.last;
      if (entry is File &&
          name.startsWith('archive_') &&
          name.endsWith('.log')) {
        final modified = await entry.lastModified();
        if (modified.isBefore(cutoff)) {
          await files.delete(entry);
        } else {
          retained.add((entry, modified));
        }
      }
    }
    retained.sort((a, b) {
      final order = a.$2.compareTo(b.$2);
      return order == 0 ? a.$1.path.compareTo(b.$1.path) : order;
    });
    for (
      var index = 0;
      index < retained.length - config.maxRotatedFiles;
      index++
    ) {
      await files.delete(retained[index].$1);
    }
  }

  Future<void> _closeWriter() async {
    final writer = _writer;
    if (writer == null) return;
    Object? failure;
    StackTrace? failureStack;
    try {
      await writer.flush();
    } on FileSystemException catch (error, stack) {
      failure = error;
      failureStack = stack;
    }
    try {
      await writer.close();
      _writer = null;
    } on FileSystemException catch (cleanup) {
      if (failure != null)
        throw DwyLogCleanupFailure(operation: failure, cleanup: cleanup);
      rethrow;
    }
    if (failure != null) Error.throwWithStackTrace(failure, failureStack!);
  }

  Future<void> close() => _closing ??= _append(() async {
    try {
      await _closeWriter();
    } finally {
      await _logger.close();
    }
  });
}

final class _LineOutput extends backend.LogOutput {
  final List<String> _lines = [];
  @override
  void output(backend.OutputEvent event) => _lines.addAll(event.lines);
  List<String> take() {
    final result = List<String>.of(_lines);
    _lines.clear();
    return result;
  }
}

final class _JsonPrinter extends backend.LogPrinter {
  @override
  List<String> log(backend.LogEvent event) => [jsonEncode(event.message)];
}

Object? _redactValue(Object? value) {
  if (value is Map<Object?, Object?>) {
    return value.map((Object? key, Object? child) {
      final name = key.toString();
      final normalized = name.toLowerCase().replaceAll(RegExp('[^a-z]'), '');
      final sensitive = [
        'authorization',
        'cookie',
        'token',
        'password',
        'passwd',
        'secret',
        'apikey',
      ].any(normalized.contains);
      return MapEntry(name, sensitive ? '[REDACTED]' : _redactValue(child));
    });
  }
  if (value is Iterable<Object?>) return value.map(_redactValue).toList();
  if (value is String) return _redactText(value);
  if (value is num) return value.isFinite ? value : value.toString();
  if (value == null || value is bool) return value;
  // Arbitrary objects may expose credentials through toString().
  return '<${value.runtimeType}>';
}

String _redactText(String value) {
  var result = value.replaceAll(
    RegExp(
      r'''\b(?:authorization|set-cookie|cookie)\b["']?\s*[:=][^\r\n]*''',
      caseSensitive: false,
    ),
    '[REDACTED]',
  );
  result = result.replaceAll(
    RegExp(r'\bBearer\s+[^\s,;]+', caseSensitive: false),
    'Bearer [REDACTED]',
  );
  result = result.replaceAll(
    RegExp(
      r'''\b(?:access[_-]?token|refresh[_-]?token|token|password|passwd|secret|api[_-]?key)\b["']?\s*[:=]\s*(?:"[^"]*"|'[^']*'|[^\s,;]+)''',
      caseSensitive: false,
    ),
    '[REDACTED]',
  );
  return result.replaceAllMapped(
    RegExp(r'https?://[^\s"<>]+', caseSensitive: false),
    (match) {
      final uri = Uri.tryParse(match.group(0)!);
      if (uri == null || !uri.hasAuthority) return '[REDACTED URL]';
      return Uri(
        scheme: uri.scheme,
        host: uri.host,
        port: uri.hasPort ? uri.port : null,
        path: uri.path,
      ).toString();
    },
  );
}
