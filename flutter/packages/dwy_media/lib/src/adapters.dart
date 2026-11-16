import 'dart:typed_data';

import 'models.dart';

/// Native integration seam for tests/host substitutions. Implementations must
/// return DWY types, preserve permission scope, and report platform failures.
abstract interface class DwyPhotoLibraryAdapter {
  Future<DwyMediaAccess> permission(DwyMediaKind kind);
  Future<DwyMediaAccess> requestAccess(DwyMediaKind kind);
  Future<void> manageLimitedAccess(DwyMediaKind kind);
  Future<List<DwyAlbum>> albums(DwyMediaKind kind);
  Future<List<DwyMediaAsset>> assets(DwyAlbum album, int page, int size);
  Future<Uint8List?> thumbnail(DwyMediaAsset asset, int width, int height);
  Future<DwyMediaFile?> open(DwyMediaAsset asset);
}

/// Picker integration seam. Empty lists/null mean user cancellation, not failure.
/// recoverLostData is an Android startup operation, not a second picker launch.
abstract interface class DwySystemMediaPickerAdapter {
  Future<List<DwyMediaFile>> pickImages(bool multiple);
  Future<List<DwyMediaFile>> pickMedia(bool multiple);
  Future<DwyMediaFile?> takePhoto();
  Future<List<DwyMediaFile>> recoverLostData();
}
