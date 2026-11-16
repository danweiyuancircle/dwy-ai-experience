import 'dart:async';

import 'package:flutter/painting.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

/// Owns one disk and memory-cache namespace in the current isolate.
/// Use a product/account-specific non-secret namespace and dispose all consumers
/// before clearing or closing it. A namespace may have only one live owner.
final class DwyImageCache {
  factory DwyImageCache({
    required String namespace,
    Duration maxIdle = const Duration(days: 7),
    int maxObjects = 200,
  }) => _create(
    namespace,
    maxIdle,
    maxObjects,
    (key) => Config(key, stalePeriod: maxIdle, maxNrOfCacheObjects: maxObjects),
  );

  /// Advanced storage injection for sandboxed tests or application-owned stores.
  /// The supplied repository and filesystem must be dedicated to this namespace.
  factory DwyImageCache.custom({
    required String namespace,
    required CacheInfoRepository repository,
    required FileSystem fileSystem,
    FileService? fileService,
    Duration maxIdle = const Duration(days: 7),
    int maxObjects = 200,
  }) => _create(
    namespace,
    maxIdle,
    maxObjects,
    (key) => fileService == null
        ? Config(
            key,
            stalePeriod: maxIdle,
            maxNrOfCacheObjects: maxObjects,
            repo: repository,
            fileSystem: fileSystem,
          )
        : Config(
            key,
            stalePeriod: maxIdle,
            maxNrOfCacheObjects: maxObjects,
            repo: repository,
            fileSystem: fileSystem,
            fileService: fileService,
          ),
  );

  DwyImageCache._(this.namespace, this._manager);

  static final Set<String> _owners = {};
  final String namespace;
  final _ManagedCache _manager;
  final Map<String, Set<ImageProvider<Object>>> _providers = {};
  Future<void>? _closing;

  static DwyImageCache _create(
    String namespace,
    Duration maxIdle,
    int maxObjects,
    Config Function(String key) configure,
  ) {
    if (!RegExp(r'^[A-Za-z0-9_-]{1,80}$').hasMatch(namespace)) {
      throw ArgumentError.value(
        namespace,
        'namespace',
        'Use 1–80 non-secret letters, digits, underscores or hyphens.',
      );
    }
    if (maxIdle <= Duration.zero || maxObjects < 1) {
      throw ArgumentError('Cache limits must be positive.');
    }
    if (!_owners.add(namespace)) {
      throw StateError('This image namespace already has a live owner.');
    }
    try {
      final config = configure('dwy_image_$namespace');
      return DwyImageCache._(namespace, _ManagedCache(config));
    } catch (_) {
      _owners.remove(namespace);
      rethrow;
    }
  }

  /// Cache identifier used by source providers; headers are intentionally absent.
  /// A changed user/security context must use a different namespace.
  String keyFor(Uri uri) {
    ensureOpen();
    return 'dwy_image:$namespace:${uri.toString()}';
  }

  /// Package-internal cache adapter. Applications should use DwyImageSource.
  BaseCacheManager get manager {
    ensureOpen();
    return _manager;
  }

  /// Records only providers created through this package for scoped eviction.
  void track(String key, ImageProvider<Object> provider) {
    ensureOpen();
    (_providers[key] ??= {}).add(provider);
  }

  /// Rejects accidental reuse after account teardown.
  void ensureOpen() {
    if (_closing != null) throw StateError('Image cache is closed.');
  }

  /// Waits for ongoing cache reads, then evicts all decoded sizes and the disk file.
  /// Unmount consumers first; mounted images may otherwise request the image again.
  Future<void> invalidate(Uri uri) {
    final key = keyFor(uri);
    return _manager.maintain(() async {
      final providers = _providers.remove(key) ?? {};
      for (final provider in providers) {
        await provider.evict();
      }
      await _manager.removeFile(key);
    });
  }

  /// Clears this namespace only, without touching Flutter's global image cache.
  /// Consumers must be unmounted before clearing private images on logout.
  Future<void> clear() {
    ensureOpen();
    return _manager.maintain(() async {
      await _evictTracked();
      await _manager.emptyCache();
    });
  }

  /// Stops new cache reads, waits for existing streams and closes the repository.
  /// Does not delete disk data; call clear before dispose when that is required.
  Future<void> dispose() => _closing ??= _manager.maintain(() async {
    await _evictTracked();
    await _manager.dispose();
    _owners.remove(namespace);
  }, closing: true);

  Future<void> _evictTracked() async {
    final providers = _providers.values.expand((value) => value).toSet();
    _providers.clear();
    for (final provider in providers) {
      await provider.evict();
    }
  }
}

final class _ManagedCache extends CacheManager {
  _ManagedCache(super.config);

  // Upstream 3.5.0 closes the repository before open completes; the store waits.
  @override
  Future<void> dispose() => store.dispose();

  final Set<Completer<void>> _reads = {};
  Future<void> _tail = Future<void>.value();
  int _maintenance = 0;
  bool _closed = false;

  @override
  Stream<FileResponse> getFileStream(
    String url, {
    String? key,
    Map<String, String>? headers,
    bool withProgress = false,
  }) async* {
    if (_closed || _maintenance > 0)
      throw StateError('Image cache is not accepting reads.');
    final done = Completer<void>();
    _reads.add(done);
    try {
      yield* super.getFileStream(
        url,
        key: key,
        headers: headers,
        withProgress: withProgress,
      );
    } finally {
      _reads.remove(done);
      done.complete();
    }
  }

  Future<void> maintain(
    Future<void> Function() action, {
    bool closing = false,
  }) {
    if (_closed)
      return Future<void>.error(StateError('Image cache is closed.'));
    _maintenance++;
    if (closing) _closed = true;
    final result = _tail
        .then((_) async {
          await Future.wait(_reads.map((read) => read.future));
          await action();
        })
        .whenComplete(() {
          _maintenance--;
        });
    // Report maintenance failures to the caller without losing the cleanup queue.
    _tail = result.then<void>((_) {}, onError: (Object _, StackTrace __) {});
    return result;
  }
}
