import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:dwy_log/dwy_log.dart';
import 'package:dwy_network/dwy_network.dart';
import 'package:dio/dio.dart' as dio;
import 'package:test/test.dart';

void main() {
  late HttpServer server;
  late DwyHttpClient client;
  late Directory directory;
  final received = <HttpRequest>[];

  setUp(() async {
    received.clear();
    directory = await Directory.systemTemp.createTemp('dwy-network-test-');
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((request) async {
      received.add(request);
      switch (request.uri.path) {
        case '/json':
          request.response.headers.contentType = ContentType.json;
          request.response.write(jsonEncode({'value': 42}));
        case '/invalid':
          request.response.headers.contentType = ContentType.json;
          request.response.write('{broken');
        case '/fail':
          request.response.statusCode = 503;
          request.response.headers.contentType = ContentType.json;
          request.response.write(jsonEncode({'code': 'unavailable'}));
        case '/redirect':
          request.response.statusCode = 302;
          request.response.headers.set(
            'location',
            'http://localhost:${server.port}/json',
          );
        case '/slow':
          await Future<void>.delayed(const Duration(milliseconds: 200));
          request.response.write('slow');
        case '/download':
          final bytes = List<int>.generate(32768, (index) => index % 256);
          request.response.contentLength = bytes.length;
          request.response.add(bytes);
        case '/upload':
          final body = await utf8.decoder.bind(request).join();
          request.response.headers.contentType = ContentType.json;
          request.response.write(
            jsonEncode({'hasFile': body.contains('file-content')}),
          );
        default:
          request.response.statusCode = 404;
      }
      await request.response.close();
    });
    client = DwyHttpClient(
      DwyHttpConfig(baseUrl: Uri.parse('http://127.0.0.1:${server.port}/')),
    );
  });
  tearDown(() async {
    await client.close();
    await server.close(force: true);
    await directory.delete(recursive: true);
  });

  test('decodes product-specific JSON without a fixed envelope', () async {
    final response = await client.request<int>(
      'json',
      decode: (value) => (value as Map<String, dynamic>)['value'] as int,
    );
    expect(response.data, 42);
    expect(response.statusCode, 200);
  });

  test(
    'distinguishes protocol failure, HTTP failure and cancellation',
    () async {
      await expectLater(
        client.request<Object?>('invalid', decode: (value) => value),
        throwsA(
          isA<DwyNetworkException>().having(
            (error) => error.kind,
            'kind',
            DwyNetworkErrorKind.decode,
          ),
        ),
      );
      await expectLater(
        client.request<Object?>('fail', decode: (value) => value),
        throwsA(
          isA<DwyNetworkException>().having(
            (error) => error.statusCode,
            'status',
            503,
          ),
        ),
      );
      final cancellation = DwyRequestCancellation();
      final request = client.request<Object?>(
        'slow',
        decode: (value) => value,
        cancellation: cancellation,
      );
      cancellation.cancel();
      await expectLater(
        request,
        throwsA(
          isA<DwyNetworkException>().having(
            (error) => error.kind,
            'kind',
            DwyNetworkErrorKind.cancelled,
          ),
        ),
      );
    },
  );

  test(
    'rejects other origins and does not follow redirects with credentials',
    () async {
      await expectLater(
        client.request<Object?>(
          'http://localhost:${server.port}/json',
          decode: (value) => value,
        ),
        throwsArgumentError,
      );
      expect(received, isEmpty);
      await expectLater(
        client.request<Object?>(
          'redirect',
          headers: {'Authorization': 'Bearer test'},
          decode: (value) => value,
        ),
        throwsA(isA<DwyNetworkException>()),
      );
      expect(received.map((request) => request.uri.path), ['/redirect']);
    },
  );

  test('does not replay failed writes and reports receive timeout', () async {
    await expectLater(
      client.request<Object?>(
        'fail',
        method: 'POST',
        data: 'once',
        decode: (value) => value,
      ),
      throwsA(isA<DwyNetworkException>()),
    );
    expect(received.where((request) => request.uri.path == '/fail').length, 1);
    final short = DwyHttpClient(
      DwyHttpConfig(
        baseUrl: Uri.parse('http://127.0.0.1:${server.port}/'),
        receiveTimeout: const Duration(milliseconds: 20),
      ),
    );
    try {
      await expectLater(
        short.request<Object?>('slow', decode: (value) => value),
        throwsA(
          isA<DwyNetworkException>().having(
            (error) => error.kind,
            'kind',
            DwyNetworkErrorKind.timeout,
          ),
        ),
      );
    } finally {
      await short.close();
    }
  });

  test('download reports real bytes into its own directory', () async {
    var bytes = 0;
    final destination = await client.download(
      'download',
      parent: directory,
      onProgress: (count, total) => bytes = count,
    );
    expect(await destination.length(), 32768);
    expect(bytes, 32768);
    expect(destination.parent.parent.path, directory.path);
    await destination.parent.delete(recursive: true);
    expect(await directory.list().toList(), isEmpty);
  });

  test(
    'concurrent downloads never overwrite files in their shared parent',
    () async {
      final destination = File('${directory.path}/created-later.bin');
      final results = await Future.wait([
        client.download(
          'download',
          parent: directory,
          onProgress: (count, total) {
            if (count == total) destination.writeAsStringSync('user-data');
          },
        ),
        client.download('download', parent: directory),
      ]);
      expect(await destination.readAsString(), 'user-data');
      expect(results.map((file) => file.path).toSet(), hasLength(2));
      for (final file in results) {
        expect(await file.length(), 32768);
        await file.parent.delete(recursive: true);
      }
    },
  );

  test('failed and cancelled downloads do not leave a final file', () async {
    await expectLater(
      client.download('fail', parent: directory),
      throwsA(isA<DwyNetworkException>()),
    );
    final cancellation = DwyRequestCancellation()..cancel();
    await expectLater(
      client.download('slow', parent: directory, cancellation: cancellation),
      throwsA(isA<DwyNetworkException>()),
    );
    expect(await directory.list().toList(), isEmpty);
  });

  test(
    'preserves product failure payload and cause without unsafe error text',
    () async {
      try {
        await client.request<Object?>('fail', decode: (value) => value);
        fail('Expected HTTP failure.');
      } on DwyNetworkException catch (error, stack) {
        expect(error.responseData, {'code': 'unavailable'});
        expect(error.cause, isNotNull);
        expect(stack.toString(), isNotEmpty);
        expect(error.toString(), isNot(contains('unavailable')));
      }
    },
  );

  test('upload sends multipart file and real progress', () async {
    final source = File('${directory.path}/source.txt');
    await source.writeAsString('file-content');
    var sent = 0;
    final response = await client.upload<bool>(
      'upload',
      files: [DwyUploadFile(field: 'file', file: source)],
      decode: (value) => (value as Map<String, dynamic>)['hasFile'] as bool,
      onProgress: (count, total) => sent = count,
    );
    expect(response.data, isTrue);
    expect(sent, greaterThan(await source.length()));
  });

  test(
    'network diagnostics omit request credentials, queries and bodies',
    () async {
      final logger = await DwyLogger.open(
        DwyLogConfig(
          directory: Directory('${directory.path}/logs'),
          minimumLevel: DwyLogLevel.debug,
        ),
      );
      final logged = DwyHttpClient(
        DwyHttpConfig(
          baseUrl: Uri.parse('http://127.0.0.1:${server.port}/'),
          headers: {'Authorization': 'Bearer header-secret'},
        ),
        logger: logger,
      );
      try {
        await logged.request<Object?>(
          'json?token=query-secret',
          method: 'POST',
          data: {'password': 'body-secret'},
          decode: (value) => value,
        );
        await logger.flush();
        final text = await File('${directory.path}/logs/latest.log')
            .readAsString();
        expect(text, contains('HTTP request'));
        for (final secret in ['header-secret', 'query-secret', 'body-secret']) {
          expect(text, isNot(contains(secret)));
        }
      } finally {
        await logged.close();
        await logger.close();
      }
    },
  );

  test(
    'close cancels and awaits active requests, rejects later work',
    () async {
      final pending = client.request<Object?>('slow', decode: (value) => value);
      final expectation = expectLater(
        pending,
        throwsA(isA<DwyNetworkException>()),
      );
      await client.close();
      await expectation;
      await expectLater(
        client.request<Object?>('json', decode: (value) => value),
        throwsStateError,
      );
    },
  );

  test(
    'response diagnostics cannot turn an accepted POST into failure',
    () async {
      final logger = await DwyLogger.open(
        DwyLogConfig(
          directory: Directory('${directory.path}/post-logs'),
          minimumLevel: DwyLogLevel.debug,
        ),
      );
      final logged = DwyHttpClient(
        DwyHttpConfig(baseUrl: Uri.parse('http://127.0.0.1:${server.port}/')),
        logger: logger,
      );
      final failures = <DwyNetworkDiagnosticFailure>[];
      final subscription = logged.diagnosticFailures.listen(failures.add);
      Future<void>? closingLogger;
      try {
        final response = await logged.request<int>(
          'json',
          method: 'POST',
          data: {'action': 'once'},
          decode: (value) {
            closingLogger = logger.close();
            return (value as Map<String, dynamic>)['value'] as int;
          },
        );
        await closingLogger;
        await logged.close();
        expect(response.data, 42);
        expect(
          received.where((request) => request.method == 'POST'),
          hasLength(1),
        );
        expect(failures.map((failure) => failure.stage), contains('response'));
      } finally {
        await subscription.cancel();
        await logged.close();
        await logger.close();
      }
    },
  );

  test(
    'HTTP and cancellation failures survive an unavailable diagnostic sink',
    () async {
      final logger = await DwyLogger.open(
        DwyLogConfig(directory: Directory('${directory.path}/failed-logs')),
      );
      await logger.close();
      final logged = DwyHttpClient(
        DwyHttpConfig(baseUrl: Uri.parse('http://127.0.0.1:${server.port}/')),
        logger: logger,
      );
      final failures = <DwyNetworkDiagnosticFailure>[];
      final subscription = logged.diagnosticFailures.listen(failures.add);
      try {
        await expectLater(
          logged.request<Object?>('fail', decode: (value) => value),
          throwsA(
            isA<DwyNetworkException>().having(
              (error) => error.kind,
              'kind',
              DwyNetworkErrorKind.response,
            ),
          ),
        );
        final cancellation = DwyRequestCancellation()..cancel();
        await expectLater(
          logged.request<Object?>(
            'slow',
            decode: (value) => value,
            cancellation: cancellation,
          ),
          throwsA(
            isA<DwyNetworkException>().having(
              (error) => error.kind,
              'kind',
              DwyNetworkErrorKind.cancelled,
            ),
          ),
        );
        await logged.close();
        expect(
          failures.where((failure) => failure.stage == 'failure'),
          hasLength(2),
        );
      } finally {
        await subscription.cancel();
        await logged.close();
      }
    },
  );

  test('transform timeout remains a timeout classification', () async {
    client.transport.interceptors.add(
      dio.InterceptorsWrapper(
        onRequest: (options, handler) {
          handler.reject(
            dio.DioException(
              requestOptions: options,
              type: dio.DioExceptionType.transformTimeout,
            ),
          );
        },
      ),
    );
    await expectLater(
      client.request<Object?>('json', decode: (value) => value),
      throwsA(
        isA<DwyNetworkException>().having(
          (error) => error.kind,
          'kind',
          DwyNetworkErrorKind.timeout,
        ),
      ),
    );
  });
}
