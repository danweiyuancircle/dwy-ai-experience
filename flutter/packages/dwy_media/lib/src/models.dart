import 'dart:typed_data';

/// Media scope requested by one operation; mixed means images and videos only.
enum DwyMediaKind { images, videos, mixed }

/// Limited access is readable, but covers only the user's visible selection.
enum DwyMediaAccess {
  notDetermined,
  restricted,
  denied,
  authorized,
  limited;

  bool get canRead => this == authorized || this == limited;
}

/// Album metadata is a snapshot. IDs belong to one device and may stop resolving
/// after deletion or a permission change; count is not a pagination guarantee.
class DwyAlbum {
  const DwyAlbum({
    required this.id,
    required this.name,
    required this.count,
    required this.kind,
    required this.isAll,
  });

  final String id;
  final String name;
  final int count;
  final DwyMediaKind kind;
  final bool isAll;
}

/// Asset identity and dimensions; no assumption that a permanent local file
/// exists. Images use Duration.zero. Opening an iCloud item can require network.
class DwyMediaAsset {
  const DwyMediaAsset({
    required this.id,
    required this.kind,
    required this.width,
    required this.height,
    required this.duration,
  });

  final String id;
  final DwyMediaKind kind;
  final int width;
  final int height;
  final Duration duration;
}

/// A zero-based page. A full page may have a following page; only a short page
/// establishes the end. Album changes can affect later page-based reads.
class DwyMediaPage {
  DwyMediaPage({
    required List<DwyMediaAsset> items,
    required this.page,
    required this.size,
  }) : items = List.unmodifiable(items);

  final List<DwyMediaAsset> items;
  final int page;
  final int size;

  bool get mayHaveMore => items.length == size;
  int? get nextPage => mayHaveMore ? page + 1 : null;
}

/// A session-scoped readable resource. Consume/copy it promptly; paths are not
/// exposed because picker caches, content resources and iCloud exports expire.
/// The name is external metadata: callers must sanitize it before filesystem use.
abstract interface class DwyMediaFile {
  String get name;
  Future<int> length();
  Stream<List<int>> openRead();
  Future<Uint8List> readAsBytes();
}

/// An expected platform/access failure. code is machine-readable; cause is kept
/// for diagnostics and must not be blindly rendered or logged with user data.
class DwyMediaException implements Exception {
  const DwyMediaException(this.code, {this.cause});

  final String code;
  final Object? cause;

  @override
  String toString() => 'DwyMediaException($code)';
}
