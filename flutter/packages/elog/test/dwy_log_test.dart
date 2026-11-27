import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:dwy_log/dwy_log.dart';
import 'package:test/test.dart';

void main() {
  late Directory directory;
  DwyLogger? log;

  setUp(() async {
    directory = await Directory.systemTemp.createTemp('dwy-log-test-');
  });
  tearDown(() async {
    await log?.close();
    log = null;
    await directory.delete(recursive: true);
  });

  test('flush preserves category, fields and hides credentials', () async {
    log = await DwyLogger.open(DwyLogConfig(directory: directory));
    await log!
        .category('network')
        .info(
          'Authorization: Bearer message-secret',
          fields: {
            'status': 200,
            'headers': {
              'Authorization': 'Bearer field-secret',
              'Cookie': 'sid=cookie-secret',
            },
            'url': 'https://user:pass@example.com/path?token=query-secret',
          },
        );
    await log!.flush();
    final text = await File('${directory.path}/latest.log').readAsString();
    final record = jsonDecode(text.trim()) as Map<String, dynamic>;
    expect(record['category'], 'network');
    expect((record['fields'] as Map<String, dynamic>)['status'], 200);
    for (final secret in [
      'message-secret',
      'field-secret',
      'cookie-secret',
      'query-secret',
      'user:pass',
    ]) {
      expect(text, isNot(contains(secret)));
    }
    expect(text, contains('[REDACTED]'));
  });

  test(
    'minimum level filters records and close drains the last write',
    () async {
      log = await DwyLogger.open(
        DwyLogConfig(directory: directory, minimumLevel: DwyLogLevel.warning),
      );
      await log!.debug('hidden');
      await log!.warning('retained');
      await log!.close();
      final text = await File('${directory.path}/latest.log').readAsString();
      expect(text, isNot(contains('hidden')));
      expect(text, contains('retained'));
      await expectLater(log!.info('after close'), throwsStateError);
    },
  );

  test(
    'recognizes common JSON credential messages and finite number fields',
    () async {
      log = await DwyLogger.open(DwyLogConfig(directory: directory));
      await log!.info(
        '{"password":"message-password","accessToken":"message-token"}',
        fields: {'measurement': double.nan},
      );
      await log!.flush();
      final text = await File('${directory.path}/latest.log').readAsString();
      expect(text, isNot(contains('message-password')));
      expect(text, isNot(contains('message-token')));
      expect((jsonDecode(text.trim()) as Map<String, dynamic>)['fields'], {
        'measurement': 'NaN',
      });
    },
  );

  test(
    'serialized file output rotates and retains configured archive count',
    () async {
      log = await DwyLogger.open(
        DwyLogConfig(
          directory: directory,
          maxFileSizeKB: 1,
          maxRotatedFiles: 2,
        ),
      );
      for (var i = 0; i < 4; i++) {
        await log!.info('record $i ${List.filled(1400, 'x').join()}');
        await log!.flush();
      }
      final files = await directory
          .list()
          .where((entry) => entry.path.endsWith('.log'))
          .toList();
      expect(files.length, lessThanOrEqualTo(3));
      expect(files.any((entry) => entry.path.contains('archive_')), isTrue);
    },
  );

  test('export creates a snapshot without overwriting user files', () async {
    log = await DwyLogger.open(DwyLogConfig(directory: directory));
    await log!.info('before export');
    final destination = await Directory.systemTemp.createTemp(
      'dwy-log-export-',
    );
    try {
      final snapshot = await log!.exportTo(destination);
      expect(
        await File('${snapshot.path}/latest.log').readAsString(),
        contains('before export'),
      );
      await log!.info('after export');
      await log!.flush();
      expect(
        await File('${directory.path}/latest.log').readAsString(),
        contains('after export'),
      );
      expect(
        await File('${snapshot.path}/latest.log').readAsString(),
        isNot(contains('after export')),
      );
    } finally {
      await destination.delete(recursive: true);
    }
  });

  test(
    'retention deletes only expired archives in an owned directory',
    () async {
      final old = File('${directory.path}/archive_old.log');
      await old.writeAsString('old');
      await old.setLastModified(
        DateTime.now().subtract(const Duration(days: 10)),
      );
      log = await DwyLogger.open(
        DwyLogConfig(directory: directory, retention: const Duration(days: 7)),
      );
      expect(await old.exists(), isFalse);
    },
  );

  test('refuses directories containing unrelated files', () async {
    await File('${directory.path}/important.txt').writeAsString('keep');
    await expectLater(
      DwyLogger.open(DwyLogConfig(directory: directory)),
      throwsArgumentError,
    );
    expect(
      await File('${directory.path}/important.txt').readAsString(),
      'keep',
    );
  });

  test(
    'redacts mixed-case URL schemes in messages fields and stacks',
    () async {
      log = await DwyLogger.open(DwyLogConfig(directory: directory));
      const address =
          'HTTPS://alice:p4ss@example.com/path?signature=signed-value';
      await log!.error(
        address,
        fields: {
          'nested': {'url': address},
        },
        stackTrace: StackTrace.fromString('at $address'),
      );
      await log!.flush();
      final text = await File('${directory.path}/latest.log').readAsString();
      for (final secret in ['alice', 'p4ss', 'signed-value', 'signature']) {
        expect(text, isNot(contains(secret)));
      }
      expect(text, contains('https://example.com/path'));
    },
  );

  test(
    'export rejects dot-segment and symbolic-link aliases of log directory',
    () async {
      log = await DwyLogger.open(DwyLogConfig(directory: directory));
      final outside = await Directory.systemTemp.createTemp(
        'dwy-export-alias-',
      );
      final alias = Link('${outside.path}/alias');
      await alias.create(directory.path);
      final name = directory.uri.pathSegments
          .where((part) => part.isNotEmpty)
          .last;
      try {
        for (final target in [
          directory,
          Directory('${directory.path}/../$name'),
          Directory(alias.path),
        ]) {
          await expectLater(log!.exportTo(target), throwsArgumentError);
        }
        expect(
          await directory.list().where((entry) => entry is Directory).toList(),
          isEmpty,
        );
        await log!.info('still available');
        await log!.flush();
      } finally {
        await outside.delete(recursive: true);
      }
    },
  );

  test(
    'prune failure becomes terminal and close still releases its file',
    () async {
      final operations = _FailingDelete();
      log = await DwyLogger.open(
        DwyLogConfig(directory: directory),
        fileOperations: operations,
      );
      await log!.info('accepted before failure');
      final archive = File('${directory.path}/archive_expired.log');
      await archive.writeAsString('expired');
      await archive.setLastModified(
        DateTime.now().subtract(const Duration(days: 10)),
      );
      operations.fail = true;
      await expectLater(log!.flush(), throwsA(same(operations.failure)));
      await expectLater(
        log!.info('rejected'),
        throwsA(
          isA<DwyLogUnavailable>().having(
            (error) => error.cause,
            'root cause',
            same(operations.failure),
          ),
        ),
      );
      await log!.close();
      await expectLater(
        operations.handle!.length(),
        throwsA(isA<FileSystemException>()),
      );
    },
  );

  for (final lifecycle in ['close', 'flush', 'export']) {
    test(
      '$lifecycle waits for in-flight rotation without reopening after close',
      () async {
        final operations = _BlockingRename();
        log = await DwyLogger.open(
          DwyLogConfig(directory: directory, maxFileSizeKB: 1),
          fileOperations: operations,
        );
        final destination = await Directory.systemTemp.createTemp(
          'dwy-rotation-snapshot-',
        );
        Directory? snapshot;
        try {
          await log!.info('first ${List.filled(1400, 'x').join()}');
          final writing = log!.info('second');
          await operations.started.future;
          var complete = false;
          final ending =
              (switch (lifecycle) {
                'close' => log!.close(),
                'flush' => log!.flush(),
                _ => log!.exportTo(destination).then<void>((value) {
                  snapshot = value;
                }),
              }).whenComplete(() {
                complete = true;
              });
          await Future<void>.delayed(Duration.zero);
          expect(complete, isFalse);
          operations.release.complete();
          await writing;
          await ending;
          await log!.close();
          expect(operations.openCount, 2);
          for (final handle in operations.handles) {
            await expectLater(
              handle.length(),
              throwsA(isA<FileSystemException>()),
            );
          }
          final files = await (snapshot ?? directory)
              .list()
              .where((entry) => entry.path.endsWith('.log'))
              .toList();
          final content = (await Future.wait(
            files.map((file) => File(file.path).readAsString()),
          )).join();
          expect(content, contains('first'));
          expect(content, contains('second'));
        } finally {
          if (!operations.release.isCompleted) operations.release.complete();
          await log!.close();
          await destination.delete(recursive: true);
        }
      },
    );
  }
}

class _FailingDelete extends DwyLogFileOperations {
  final failure = const FileSystemException(
    'injected archive deletion failure',
  );
  bool fail = false;
  RandomAccessFile? handle;
  @override
  Future<RandomAccessFile> open(File file) async {
    return handle = await super.open(file);
  }

  @override
  Future<void> delete(File file) async {
    if (fail) throw failure;
    await super.delete(file);
  }
}

class _BlockingRename extends DwyLogFileOperations {
  final started = Completer<void>();
  final release = Completer<void>();
  final handles = <RandomAccessFile>[];
  int openCount = 0;
  @override
  Future<RandomAccessFile> open(File file) async {
    openCount++;
    final handle = await super.open(file);
    handles.add(handle);
    return handle;
  }

  @override
  Future<void> rename(File source, File destination) async {
    started.complete();
    await release.future;
    await super.rename(source, destination);
  }
}
