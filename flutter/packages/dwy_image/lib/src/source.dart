import 'dart:async';
import 'dart:typed_data';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/widgets.dart';

import 'cache.dart';
import 'local_file_stub.dart'
    if (dart.library.io) 'local_file_io.dart'
    as local;

/// Immutable image location. Keep memory buffers unchanged while in use.
/// Network URLs must not contain credentials; private images need an account cache.
final class DwyImageSource {
  DwyImageSource._(this._original, {DwyImageCache? cache, Uri? uri})
    : _cache = cache,
      _uri = uri;

  factory DwyImageSource.asset(
    String name, {
    String? package,
    AssetBundle? bundle,
  }) {
    if (name.trim().isEmpty) throw ArgumentError.value(name, 'name');
    return DwyImageSource._(AssetImage(name, package: package, bundle: bundle));
  }

  /// Local paths are supported on mobile/desktop, not web. File lifetime is owned
  /// by the application and must extend through image decoding.
  factory DwyImageSource.file(String path) {
    if (path.trim().isEmpty) throw ArgumentError.value(path, 'path');
    return DwyImageSource._(local.localImage(path));
  }

  factory DwyImageSource.memory(Uint8List bytes) {
    if (bytes.isEmpty)
      throw ArgumentError.value(
        bytes.length,
        'bytes',
        'Image bytes cannot be empty.',
      );
    return DwyImageSource._(MemoryImage(bytes));
  }

  factory DwyImageSource.network(
    Uri uri, {
    required DwyImageCache cache,
    Map<String, String> headers = const {},
  }) {
    if (!uri.hasAuthority ||
        !['https', 'http'].contains(uri.scheme) ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasFragment) {
      throw ArgumentError(
        'Use an absolute HTTP(S) image URL without user info or fragments.',
      );
    }
    final key = cache.keyFor(uri);
    // Upstream equality ignores headers/cacheManager; namespacing the key prevents
    // decoded images from one account being reused in another account's widget.
    return DwyImageSource._(
      CachedNetworkImageProvider(
        uri.toString(),
        cacheManager: cache.manager,
        cacheKey: key,
        headers: Map<String, String>.unmodifiable(headers),
      ),
      cache: cache,
      uri: uri,
    );
  }

  final ImageProvider<Object> _original;
  final DwyImageCache? _cache;
  final Uri? _uri;
  final Set<ImageProvider<Object>> _localVariants = {};

  /// Physical-pixel decode bounds for avatars, backgrounds or image widgets.
  /// The package does not create resized disk copies; invalidation removes the
  /// original and every decode size registered through this source/cache.
  ImageProvider<Object> provider({int? cacheWidth, int? cacheHeight}) {
    if ((cacheWidth != null && cacheWidth < 1) ||
        (cacheHeight != null && cacheHeight < 1)) {
      throw ArgumentError(
        'Decode dimensions must be positive physical pixels.',
      );
    }
    final ImageProvider<Object> image =
        cacheWidth == null && cacheHeight == null
        ? _original
        : ResizeImage(
            _original,
            width: cacheWidth,
            height: cacheHeight,
            policy: ResizeImagePolicy.fit,
          );
    if (_cache case final cache?) {
      final key = cache.keyFor(_uri!);
      cache.track(key, _original);
      cache.track(key, image);
    } else {
      _localVariants.add(image);
    }
    return image;
  }

  /// Preloads and decodes this source, returning failures to the caller.
  /// Releases its listener before completing, so account teardown need not wait
  /// for the post-frame listener release performed by Flutter's precacheImage.
  Future<void> prefetch(
    BuildContext context, {
    int? cacheWidth,
    int? cacheHeight,
  }) {
    final done = Completer<void>();
    final stream = provider(
      cacheWidth: cacheWidth,
      cacheHeight: cacheHeight,
    ).resolve(createLocalImageConfiguration(context));
    late ImageStreamListener listener;
    listener = ImageStreamListener(
      (image, synchronous) {
        stream.removeListener(listener);
        image.dispose();
        done.complete();
      },
      onError: (Object error, StackTrace? stack) {
        stream.removeListener(listener);
        done.completeError(error, stack);
      },
    );
    stream.addListener(listener);
    return done.future;
  }

  /// Invalidates this source; network variants are evicted within its scope.
  /// Local invalidation covers decode sizes registered through this source.
  Future<void> invalidate() async {
    if (_cache case final cache?) {
      await cache.invalidate(_uri!);
      return;
    }
    final providers = {..._localVariants, _original};
    _localVariants.clear();
    for (final provider in providers) {
      await provider.evict();
    }
  }

  @override
  bool operator ==(Object other) =>
      other is DwyImageSource && other._original == _original;

  @override
  int get hashCode => _original.hashCode;

  @override
  String toString() => 'DwyImageSource(${_uri == null ? 'local' : 'network'})';
}
