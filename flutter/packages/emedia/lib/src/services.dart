import 'package:flutter/services.dart';

import 'adapters.dart';
import 'models.dart';
import 'plugin_adapters.dart';

/// Album enumeration without custom UI. Prompt only from an explicit user
/// action through requestAccess; reads check current access without prompting.
class DwyPhotoLibrary {
  DwyPhotoLibrary() : _adapter = PhotoManagerAdapter();

  DwyPhotoLibrary.withAdapter(this._adapter);

  final DwyPhotoLibraryAdapter _adapter;

  Future<DwyMediaAccess> permission({required DwyMediaKind kind}) =>
      _platformCall(() => _adapter.permission(kind));

  Future<DwyMediaAccess> requestAccess({required DwyMediaKind kind}) =>
      _platformCall(() => _adapter.requestAccess(kind));

  /// Opens the OS's limited-selection manager. Refresh albums after it returns;
  /// iOS may complete before dismissal on older OS versions.
  Future<DwyMediaAccess> manageLimitedAccess({
    required DwyMediaKind kind,
  }) async {
    if (await permission(kind: kind) != DwyMediaAccess.limited) {
      throw const DwyMediaException('limited_access_required');
    }
    await _platformCall(() => _adapter.manageLimitedAccess(kind));
    return permission(kind: kind);
  }

  Future<List<DwyAlbum>> albums({required DwyMediaKind kind}) async {
    await _requireAccess(kind);
    return List.unmodifiable(await _platformCall(() => _adapter.albums(kind)));
  }

  Future<DwyMediaPage> assets(
    DwyAlbum album, {
    required int page,
    int size = 80,
  }) async {
    if (page < 0)
      throw ArgumentError.value(page, 'page', 'Must be nonnegative');
    if (size < 1 || size > 200) {
      throw ArgumentError.value(size, 'size', 'Must be between 1 and 200');
    }
    await _requireAccess(album.kind);
    final items = await _platformCall(() => _adapter.assets(album, page, size));
    return DwyMediaPage(items: items, page: page, size: size);
  }

  /// Pixel dimensions, not logical widget dimensions. Null means the thumbnail
  /// is unavailable; no placeholder bytes are fabricated.
  Future<Uint8List?> thumbnail(
    DwyMediaAsset asset, {
    required int width,
    required int height,
  }) async {
    if (width < 1 || height < 1 || width > 4096 || height > 4096) {
      throw ArgumentError(
        'Thumbnail dimensions must be between 1 and 4096 pixels',
      );
    }
    await _requireAccess(asset.kind);
    return _platformCall(() => _adapter.thumbnail(asset, width, height));
  }

  /// Resolving the original file may fetch iCloud content. No timeout or global
  /// cancel-all is imposed; the platform error/unavailability remains visible.
  Future<DwyMediaFile> open(DwyMediaAsset asset) async {
    await _requireAccess(asset.kind);
    final file = await _platformCall(() => _adapter.open(asset));
    if (file == null) throw const DwyMediaException('asset_unavailable');
    return file;
  }

  Future<void> _requireAccess(DwyMediaKind kind) async {
    if (!(await permission(kind: kind)).canRead) {
      throw const DwyMediaException('access_denied');
    }
  }
}

/// System selection/capture without pre-requesting whole-library access. The
/// caller serializes picker launches and recovers Android lost data at startup.
class DwySystemMediaPicker {
  DwySystemMediaPicker() : _adapter = ImagePickerAdapter();

  DwySystemMediaPicker.withAdapter(this._adapter);

  final DwySystemMediaPickerAdapter _adapter;

  Future<List<DwyMediaFile>> pickImages({bool multiple = false}) =>
      _pick(() => _adapter.pickImages(multiple));

  Future<List<DwyMediaFile>> pickMedia({bool multiple = false}) =>
      _pick(() => _adapter.pickMedia(multiple));

  Future<DwyMediaFile?> takePhoto() => _platformCall(_adapter.takePhoto);

  /// Android only in the default adapter; other platforms return no recovery.
  /// Invoke once at application startup, before starting another selection.
  Future<List<DwyMediaFile>> recoverLostData() =>
      _pick(_adapter.recoverLostData);

  Future<List<DwyMediaFile>> _pick(
    Future<List<DwyMediaFile>> Function() action,
  ) async => List.unmodifiable(await _platformCall(action));
}

Future<T> _platformCall<T>(Future<T> Function() action) async {
  try {
    return await action();
  } on PlatformException catch (error) {
    throw DwyMediaException(error.code, cause: error);
  }
}
