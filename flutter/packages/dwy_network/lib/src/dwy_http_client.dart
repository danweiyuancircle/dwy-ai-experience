import 'dart:async';
import 'dart:io';

import 'package:dio/dio.dart' as dio;
import 'package:dwy_log/dwy_log.dart';

/// Stable transport failures; server business codes remain in product repositories.
enum DwyNetworkErrorKind {
  cancelled,
  timeout,
  connection,
  certificate,
  response,
  decode,
  unknown,
}

/// Safe diagnostic summary; [responseData] and [cause] are available for explicit inspection.
/// Never log these fields directly: failures may contain sensitive data.
final class DwyNetworkException implements Exception {
  const DwyNetworkException(
    this.kind, {
    this.statusCode,
    this.responseData,
    this.cause,
  });
  final DwyNetworkErrorKind kind;
  final int? statusCode;
  final Object? responseData;
  final Object? cause;

  @override
  String toString() =>
      'DwyNetworkException(${kind.name}${statusCode == null ? '' : ', HTTP $statusCode'})';
}

/// A diagnostic sink failure, separate from the HTTP operation's result.
/// Inspect [cause] explicitly; its text may contain private filesystem metadata.
final class DwyNetworkDiagnosticFailure {
  const DwyNetworkDiagnosticFailure({
    required this.requestId,
    required this.stage,
    required this.cause,
    required this.stackTrace,
  });
  final int requestId;
  final String stage;
  final Object cause;
  final StackTrace stackTrace;
}

/// Preserves a failed download and its subsequent temporary-file cleanup failure.
/// The caller may remove [directory] after inspecting both causes explicitly.
final class DwyDownloadCleanupFailure implements Exception {
  const DwyDownloadCleanupFailure({
    required this.operation,
    required this.cleanup,
    required this.directory,
  });
  final Object operation;
  final Object cleanup;
  final Directory directory;
  @override
  String toString() => 'DwyDownloadCleanupFailure';
}

/// Cancels one request or a caller-owned group without affecting other clients.
final class DwyRequestCancellation {
  final dio.CancelToken _token = dio.CancelToken();

  bool get isCancelled => _token.isCancelled;

  /// Cancellation is reported as [DwyNetworkErrorKind.cancelled], not success.
  void cancel() => _token.cancel();
}

/// One service configuration. Use separate clients for cloud and device services.
final class DwyHttpConfig {
  DwyHttpConfig({
    required this.baseUrl,
    Map<String, Object?> headers = const {},
    this.connectTimeout = const Duration(seconds: 15),
    this.sendTimeout = const Duration(seconds: 30),
    this.receiveTimeout = const Duration(seconds: 30),
  }) : headers = Map.unmodifiable(headers) {
    if (!['http', 'https'].contains(baseUrl.scheme) ||
        baseUrl.host.isEmpty ||
        baseUrl.userInfo.isNotEmpty ||
        baseUrl.hasQuery ||
        baseUrl.hasFragment) {
      throw ArgumentError(
        'Use an absolute HTTP(S) service URL without credentials, query or fragment.',
      );
    }
    for (final timeout in [connectTimeout, sendTimeout, receiveTimeout]) {
      if (timeout <= Duration.zero)
        throw ArgumentError('Timeouts must be positive.');
    }
  }

  final Uri baseUrl;
  final Map<String, Object?> headers;
  final Duration connectTimeout;
  final Duration sendTimeout;
  final Duration receiveTimeout;
}

/// Decoded payload plus HTTP metadata; no fixed backend envelope is assumed.
final class DwyHttpResponse<T> {
  DwyHttpResponse({
    required this.data,
    required this.statusCode,
    required Map<String, List<String>> headers,
  }) : headers = Map.unmodifiable(
         headers.map(
           (key, value) => MapEntry(key, List<String>.unmodifiable(value)),
         ),
       );
  final T data;
  final int? statusCode;
  final Map<String, List<String>> headers;
}

/// Caller-selected upload file. The caller retains access until upload completes.
final class DwyUploadFile {
  const DwyUploadFile({required this.field, required this.file, this.fileName});
  final String field;
  final File file;
  final String? fileName;
}

/// Isolated service client; normal APIs reject cross-origin URLs and redirects.
/// Close before closing the shared logger; no implicit retry or token refresh.
final class DwyHttpClient {
  DwyHttpClient(this.config, {DwyLogger? logger})
    : _logger = logger?.category('network'),
      _transport = dio.Dio(
        dio.BaseOptions(
          baseUrl: config.baseUrl.toString(),
          headers: config.headers,
          connectTimeout: config.connectTimeout,
          sendTimeout: config.sendTimeout,
          receiveTimeout: config.receiveTimeout,
          followRedirects: false,
        ),
      );

  final DwyHttpConfig config;
  final DwyLogger? _logger;
  final dio.Dio _transport;
  final Set<Completer<void>> _active = {};
  final StreamController<DwyNetworkDiagnosticFailure> _diagnosticFailures =
      StreamController<DwyNetworkDiagnosticFailure>.broadcast();
  Future<void>? _closing;
  var _sequence = 0;

  /// Observe logging failures without changing HTTP success/failure semantics.
  /// Subscribe before requests; cancel or resume paused subscriptions before close.
  Stream<DwyNetworkDiagnosticFailure> get diagnosticFailures =>
      _diagnosticFailures.stream;

  /// Advanced escape hatch for adapters, interceptors and streaming.
  /// Direct calls bypass DWY origin checks, lifecycle tracking and safe logging.
  dio.Dio get transport => _transport;

  /// Performs JSON HTTP and delegates payload validation to [decode].
  Future<DwyHttpResponse<T>> request<T>(
    String path, {
    required T Function(Object? value) decode,
    String method = 'GET',
    Object? data,
    Map<String, Object?>? queryParameters,
    Map<String, Object?>? headers,
    DwyRequestCancellation? cancellation,
  }) => _perform(() async {
    final target = _target(path);
    if (!RegExp(r'^[A-Z]+$').hasMatch(method))
      throw ArgumentError.value(
        method,
        'method',
        'Use an uppercase HTTP method.',
      );
    return _diagnose(method, target, () async {
      final response = await _transport.request<Object?>(
        target.toString(),
        data: data,
        queryParameters: queryParameters,
        options: dio.Options(
          method: method,
          headers: headers,
          responseType: dio.ResponseType.json,
        ),
        cancelToken: cancellation?._token,
      );
      return _decode(response, decode);
    });
  });

  /// Sends multipart content; progress counts actual transmitted multipart bytes.
  Future<DwyHttpResponse<T>> upload<T>(
    String path, {
    required List<DwyUploadFile> files,
    required T Function(Object? value) decode,
    Map<String, String> fields = const {},
    Map<String, Object?>? headers,
    DwyRequestCancellation? cancellation,
    void Function(int sent, int total)? onProgress,
  }) => _perform(() async {
    final target = _target(path);
    final form = dio.FormData();
    form.fields.addAll(fields.entries);
    for (final file in files) {
      if (file.field.isEmpty ||
          file.field.contains(RegExp(r'[\r\n]')) ||
          (file.fileName?.contains(RegExp(r'[\r\n]')) ?? false)) {
        throw ArgumentError(
          'Multipart names cannot be empty or contain newlines.',
        );
      }
      form.files.add(
        MapEntry(
          file.field,
          await dio.MultipartFile.fromFile(
            file.file.path,
            filename: file.fileName,
          ),
        ),
      );
    }
    return _diagnose('POST', target, () async {
      final response = await _transport.post<Object?>(
        target.toString(),
        data: form,
        options: dio.Options(
          headers: headers,
          responseType: dio.ResponseType.json,
        ),
        cancelToken: cancellation?._token,
        onSendProgress: onProgress,
      );
      return _decode(response, decode);
    });
  });

  /// Returns a complete file in a newly allocated, exclusively owned child of [parent].
  /// The caller owns the returned file's parent directory and must remove it after use.
  /// This API never commits into an arbitrary shared destination path.
  Future<File> download(
    String path, {
    required Directory parent,
    Map<String, Object?>? headers,
    DwyRequestCancellation? cancellation,
    void Function(int received, int total)? onProgress,
  }) => _perform(() async {
    final target = _target(path);
    final staging = await parent.createTemp('.dwy-download-');
    try {
      final payload = File('${staging.path}${Platform.pathSeparator}payload');
      await _diagnose('GET', target, () async {
        final response = await _transport.download(
          target.toString(),
          payload.path,
          options: dio.Options(headers: headers),
          cancelToken: cancellation?._token,
          onReceiveProgress: onProgress,
          deleteOnError: true,
        );
        return DwyHttpResponse<void>(
          data: null,
          statusCode: response.statusCode,
          headers: response.headers.map,
        );
      });
      if (_closing != null || cancellation?.isCancelled == true) {
        throw const DwyNetworkException(DwyNetworkErrorKind.cancelled);
      }
      return payload;
    } catch (error, stack) {
      // Preserve every operation failure while releasing only this owned directory.
      try {
        await staging.delete(recursive: true);
      } on FileSystemException catch (cleanup) {
        throw DwyDownloadCleanupFailure(
          operation: error,
          cleanup: cleanup,
          directory: staging,
        );
      }
      Error.throwWithStackTrace(error, stack);
    }
  });

  Uri _target(String path) {
    final target = config.baseUrl.resolve(path);
    if (!['http', 'https'].contains(target.scheme) ||
        !target.hasAuthority ||
        target.origin != config.baseUrl.origin ||
        target.userInfo.isNotEmpty ||
        target.hasFragment) {
      throw ArgumentError(
        'Request must stay within the configured service origin.',
      );
    }
    return target;
  }

  DwyHttpResponse<T> _decode<T>(
    dio.Response<Object?> response,
    T Function(Object?) decode,
  ) {
    try {
      return DwyHttpResponse(
        data: decode(response.data),
        statusCode: response.statusCode,
        headers: response.headers.map,
      );
    } on FormatException catch (error, stack) {
      Error.throwWithStackTrace(
        DwyNetworkException(DwyNetworkErrorKind.decode, cause: error),
        stack,
      );
    } on TypeError catch (error, stack) {
      Error.throwWithStackTrace(
        DwyNetworkException(DwyNetworkErrorKind.decode, cause: error),
        stack,
      );
    }
  }

  Future<T> _perform<T>(Future<T> Function() operation) async {
    if (_closing != null) throw StateError('HTTP client is closed.');
    final finished = Completer<void>();
    _active.add(finished);
    try {
      return await operation();
    } finally {
      _active.remove(finished);
      finished.complete();
    }
  }

  Future<DwyHttpResponse<T>> _diagnose<T>(
    String method,
    Uri target,
    Future<DwyHttpResponse<T>> Function() operation,
  ) async {
    final id = ++_sequence;
    final stopwatch = Stopwatch()..start();
    await _diagnoseLog(
      id,
      'request',
      DwyLogLevel.debug,
      'HTTP request',
      fields: {'request_id': id, 'method': method, 'origin': target.origin},
    );
    try {
      final response = await operation();
      await _diagnoseLog(
        id,
        'response',
        DwyLogLevel.debug,
        'HTTP response',
        fields: {
          'request_id': id,
          'status': response.statusCode,
          'duration_ms': stopwatch.elapsedMilliseconds,
        },
      );
      return response;
    } on dio.DioException catch (error) {
      final failure = DwyNetworkException(
        switch (error.type) {
          dio.DioExceptionType.cancel => DwyNetworkErrorKind.cancelled,
          dio.DioExceptionType.connectionTimeout ||
          dio.DioExceptionType.sendTimeout ||
          dio.DioExceptionType.receiveTimeout ||
          dio.DioExceptionType.transformTimeout => DwyNetworkErrorKind.timeout,
          dio.DioExceptionType.connectionError =>
            DwyNetworkErrorKind.connection,
          dio.DioExceptionType.badCertificate =>
            DwyNetworkErrorKind.certificate,
          dio.DioExceptionType.badResponse => DwyNetworkErrorKind.response,
          dio.DioExceptionType.unknown =>
            error.error is FormatException
                ? DwyNetworkErrorKind.decode
                : DwyNetworkErrorKind.unknown,
        },
        statusCode: error.response?.statusCode,
        responseData: error.response?.data,
        cause: error,
      );
      await _diagnoseLog(
        id,
        'failure',
        failure.kind == DwyNetworkErrorKind.cancelled
            ? DwyLogLevel.debug
            : DwyLogLevel.warning,
        'HTTP failure',
        fields: {
          'request_id': id,
          'kind': failure.kind.name,
          'status': failure.statusCode,
          'duration_ms': stopwatch.elapsedMilliseconds,
        },
      );
      Error.throwWithStackTrace(failure, error.stackTrace);
    }
  }

  Future<void> _diagnoseLog(
    int requestId,
    String stage,
    DwyLogLevel level,
    String message, {
    required Map<String, Object?> fields,
  }) async {
    try {
      await _logger?.log(level, message, fields: fields);
    } catch (error, stack) {
      // This boundary surrounds only diagnostics, never the HTTP operation itself.
      _diagnosticFailures.add(
        DwyNetworkDiagnosticFailure(
          requestId: requestId,
          stage: stage,
          cause: error,
          stackTrace: stack,
        ),
      );
    }
  }

  /// Cancels and waits for tracked requests; the injected logger remains caller-owned.
  Future<void> close() {
    return _closing ??= () async {
      _transport.close(force: true);
      await Future.wait(_active.map((completion) => completion.future));
      await _diagnosticFailures.close();
    }();
  }
}
