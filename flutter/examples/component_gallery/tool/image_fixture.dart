import 'dart:async';
import 'dart:io';

/// Optional loopback-only image fixture. Run with the already approved Dart SDK;
/// no external image service or user file is accessed.
Future<void> main(List<String> arguments) async {
  if (arguments.length > 1) {
    stderr.writeln('Usage: dart run tool/image_fixture.dart [PORT:1..65535]');
    exitCode = 64;
    return;
  }
  final port = arguments.isEmpty ? 5189 : int.tryParse(arguments.single);
  if (port == null || port < 1 || port > 65535) {
    stderr.writeln('Usage: dart run tool/image_fixture.dart [PORT:1..65535]');
    exitCode = 64;
    return;
  }
  final bytes = await File.fromUri(
    Platform.script.resolve('../assets/sample.png'),
  ).readAsBytes();
  final server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);
  stdout.writeln('Image: http://127.0.0.1:${server.port}/image.png');
  stdout.writeln('Delayed: http://127.0.0.1:${server.port}/slow.png');
  stdout.writeln(
    'First request fails, retry succeeds: http://127.0.0.1:${server.port}/flaky.png',
  );
  stdout.writeln('Missing: http://127.0.0.1:${server.port}/missing.png');
  var attempts = 0;
  final signal = ProcessSignal.sigint.watch().listen((_) {
    unawaited(server.close(force: true));
  });
  try {
    await for (final request in server) {
      final response = request.response;
      response.headers.set('Access-Control-Allow-Origin', '*');
      if (request.method == 'OPTIONS') {
        response.headers.set(
          'Access-Control-Allow-Methods',
          'GET, HEAD, OPTIONS',
        );
        response.statusCode = HttpStatus.noContent;
      } else if (!['GET', 'HEAD'].contains(request.method)) {
        response.statusCode = HttpStatus.methodNotAllowed;
        response.headers.set(HttpHeaders.allowHeader, 'GET, HEAD, OPTIONS');
      } else if ([
        '/image.png',
        '/slow.png',
        '/flaky.png',
      ].contains(request.uri.path)) {
        if (request.uri.path == '/slow.png') {
          await Future<void>.delayed(const Duration(seconds: 1));
        }
        if (request.uri.path == '/flaky.png' && attempts++ == 0) {
          response.statusCode = HttpStatus.serviceUnavailable;
          response.headers.set(HttpHeaders.cacheControlHeader, 'no-store');
        } else {
          response.headers.contentType = ContentType('image', 'png');
          response.headers.set(
            HttpHeaders.cacheControlHeader,
            'public, max-age=3600',
          );
          response.contentLength = bytes.length;
          if (request.method == 'GET') response.add(bytes);
        }
      } else {
        response.statusCode = HttpStatus.notFound;
      }
      await response.close();
    }
  } finally {
    await signal.cancel();
    await server.close(force: true);
  }
}
