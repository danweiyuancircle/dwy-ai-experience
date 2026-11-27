import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart'
    show TargetPlatform, defaultTargetPlatform, kIsWeb;
import 'package:image_picker/image_picker.dart';
import 'package:photo_manager/photo_manager.dart';

import 'adapters.dart';
import 'models.dart';

// Keeps native album handles/filter options inside one service instance.
class PhotoManagerAdapter implements DwyPhotoLibraryAdapter {
  final Map<(DwyMediaKind, String), AssetPathEntity> _albums = {};

  PermissionRequestOption _option(DwyMediaKind kind) => PermissionRequestOption(
    iosAccessLevel: IosAccessLevel.readWrite,
    androidPermission: AndroidPermission(
      type: _type(kind),
      mediaLocation: false,
    ),
  );

  @override
  Future<DwyMediaAccess> permission(DwyMediaKind kind) async => _access(
    await PhotoManager.getPermissionState(requestOption: _option(kind)),
  );

  @override
  Future<DwyMediaAccess> requestAccess(DwyMediaKind kind) async => _access(
    await PhotoManager.requestPermissionExtend(requestOption: _option(kind)),
  );

  @override
  Future<void> manageLimitedAccess(DwyMediaKind kind) =>
      PhotoManager.presentLimited(type: _type(kind));

  @override
  Future<List<DwyAlbum>> albums(DwyMediaKind kind) async {
    final paths = await PhotoManager.getAssetPathList(type: _type(kind));
    final result = <DwyAlbum>[];
    for (final path in paths) {
      result.add(
        DwyAlbum(
          id: path.id,
          name: path.name,
          count: await path.assetCountAsync,
          kind: kind,
          isAll: path.isAll,
        ),
      );
    }
    _albums.removeWhere((key, _) => key.$1 == kind);
    for (final path in paths) {
      _albums[(kind, path.id)] = path;
    }
    return result;
  }

  @override
  Future<List<DwyMediaAsset>> assets(DwyAlbum album, int page, int size) async {
    final path = _albums[(album.kind, album.id)];
    if (path == null) throw const DwyMediaException('album_unavailable');
    final assets = await path.getAssetListPaged(page: page, size: size);
    return assets
        .map(
          (asset) => DwyMediaAsset(
            id: asset.id,
            kind: switch (asset.type) {
              AssetType.image => DwyMediaKind.images,
              AssetType.video => DwyMediaKind.videos,
              _ => throw const DwyMediaException('unsupported_asset'),
            },
            width: asset.width,
            height: asset.height,
            duration: Duration(seconds: asset.duration),
          ),
        )
        .toList();
  }

  @override
  Future<Uint8List?> thumbnail(
    DwyMediaAsset asset,
    int width,
    int height,
  ) async {
    final entity = await AssetEntity.fromId(asset.id);
    if (entity == null) return null;
    return entity.thumbnailDataWithSize(ThumbnailSize(width, height));
  }

  @override
  Future<DwyMediaFile?> open(DwyMediaAsset asset) async {
    final entity = await AssetEntity.fromId(asset.id);
    if (entity == null) return null;
    final file = await entity.loadFile(isOrigin: true);
    if (file == null) return null;
    return _LocalMediaFile(file);
  }

  RequestType _type(DwyMediaKind kind) => switch (kind) {
    DwyMediaKind.images => RequestType.image,
    DwyMediaKind.videos => RequestType.video,
    DwyMediaKind.mixed => RequestType.common,
  };

  DwyMediaAccess _access(PermissionState state) => switch (state) {
    PermissionState.notDetermined => DwyMediaAccess.notDetermined,
    PermissionState.restricted => DwyMediaAccess.restricted,
    PermissionState.denied => DwyMediaAccess.denied,
    PermissionState.authorized => DwyMediaAccess.authorized,
    PermissionState.limited => DwyMediaAccess.limited,
  };
}

class ImagePickerAdapter implements DwySystemMediaPickerAdapter {
  final ImagePicker _picker = ImagePicker();

  @override
  Future<List<DwyMediaFile>> pickImages(bool multiple) async {
    if (multiple) {
      final files = await _picker.pickMultiImage(requestFullMetadata: false);
      return files.map(_PickerMediaFile.new).toList();
    }
    final file = await _picker.pickImage(
      source: ImageSource.gallery,
      requestFullMetadata: false,
    );
    return [if (file != null) _PickerMediaFile(file)];
  }

  @override
  Future<List<DwyMediaFile>> pickMedia(bool multiple) async {
    if (multiple) {
      final files = await _picker.pickMultipleMedia(requestFullMetadata: false);
      return files.map(_PickerMediaFile.new).toList();
    }
    final file = await _picker.pickMedia(requestFullMetadata: false);
    return [if (file != null) _PickerMediaFile(file)];
  }

  @override
  Future<DwyMediaFile?> takePhoto() async {
    final file = await _picker.pickImage(
      source: ImageSource.camera,
      requestFullMetadata: false,
    );
    return file == null ? null : _PickerMediaFile(file);
  }

  @override
  Future<List<DwyMediaFile>> recoverLostData() async {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) return [];
    final response = await _picker.retrieveLostData();
    if (response.isEmpty) return [];
    if (response.exception != null) throw response.exception!;
    final files = response.files;
    if (files != null && files.isNotEmpty)
      return files.map(_PickerMediaFile.new).toList();
    // LostDataResponse has separate single/multiple fields; either can carry the
    // one-shot result, which must not be discarded after native recovery clears it.
    final file = response.file;
    if (file != null) return [_PickerMediaFile(file)];
    throw const DwyMediaException('invalid_lost_data_response');
  }
}

class _PickerMediaFile implements DwyMediaFile {
  _PickerMediaFile(this._file);
  final XFile _file;

  @override
  String get name => _file.name;
  @override
  Future<int> length() => _file.length();
  @override
  Stream<List<int>> openRead() => _file.openRead();
  @override
  Future<Uint8List> readAsBytes() => _file.readAsBytes();
}

class _LocalMediaFile implements DwyMediaFile {
  _LocalMediaFile(this._file);
  final File _file;

  @override
  String get name => _file.uri.pathSegments.last;
  @override
  Future<int> length() => _file.length();
  @override
  Stream<List<int>> openRead() => _file.openRead();
  @override
  Future<Uint8List> readAsBytes() => _file.readAsBytes();
}
